import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
from streamlit_folium import st_folium
import pygwalker as pyg
import requests
import os
import sys
import warnings
from streamlit_option_menu import option_menu
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import joblib
from xgboost.sklearn import XGBRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error,mean_squared_error, make_scorer, r2_score

from src.mapData import get_region_mapping, get_state_mapping, get_city_mapping, get_product_mapping, get_sales_method_mapping, get_retailer_mapping, prepare_data
import src.query as query

# Hàm để đọc tất cả các file doanh thu trong thư mục
def load_all_data(fl):
    if fl is not None:
        file_name = fl.name
        _, file_extension = os.path.splitext(file_name)
        if file_extension == '.xlsx':
            df1 = pd.read_excel(fl)
        elif file_extension == '.csv':
            df1 = pd.read_csv(fl)
    result = query.view_all_data()
    df = pd.DataFrame(result, columns=["Retailer", "Region", "State", "City", "Product", "Price per Unit", "Units Sold", "Operating Profit", "Sales Method", "Total Sales", "Month", "Year", "Day", "Season", "Date", "id"])
    return pd.concat([df, df1], ignore_index=True)

def buid_model(df_combined):
    # Chuẩn hóa dữ liệu
    df_combined = df_combined.groupby(["Retailer","Region", "State", "City", "Month", "Product", "Sales Method"])["Total Sales"].sum().reset_index()
    
    region_mapping = get_region_mapping()
    state_mapping = get_state_mapping()
    city_mapping = get_city_mapping()
    product_mapping = get_product_mapping()
    sales_method_mapping = get_sales_method_mapping()
    retailer_mapping = get_retailer_mapping()
    
    df_combined = prepare_data(df_combined, region_mapping, state_mapping, city_mapping, product_mapping, retailer_mapping, sales_method_mapping)

    # Lấy các biến độc lập (features) và target cho mô hình
    features = ['Retailer','Region','State','City','Product','Sales Method','Month','Season']
    target = 'Total Sales'
    X = df_combined[features]
    y = df_combined[target]

    # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Các hyperparameters đã được tối ưu từ Bayesian Optimization
    best_hyperparameters = {
        'colsample_bytree': 0.7004047391848559,
        'gamma': 0.0,
        'learning_rate': 0.31613869711382697,
        'max_depth': 7,
        'min_child_weight': 10,
        'n_estimators': 200,
        'subsample': 1.0
    }

    # Chuyển đổi biến mục tiêu
    y_train_log = np.log1p(y_train)
    y_test_log = np.log1p(y_test)

    # Khởi tạo mô hình Decision Tree Regression với hyperparameters đã được tối ưu
    model_optimized_xgb = XGBRegressor(random_state=42, **best_hyperparameters)

    # Huấn luyện mô hình với dữ liệu huấn luyện
    model_optimized_xgb.fit(X_train, y_train_log)

    # Dự đoán trên tập test
    y_pred_log = model_optimized_xgb.predict(X_test)

    # Chuyển đổi ngược lại
    y_pred_optimized_xgb = np.expm1(y_pred_log)

    # lưu mô hình
    model_xgb = joblib.dump(model_optimized_xgb, 'model_xgb.pkl')
    # Đánh giá hiệu suất
    mse_optimized_xgb = mean_squared_error(y_test, y_pred_optimized_xgb)
    rmse_optimized_xgb = np.sqrt(mse_optimized_xgb)
    r_squared_optimized_xgb = r2_score(y_test, y_pred_optimized_xgb)

    with st.container(border=True):
        st.markdown("""
            <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Kết Quả Dự Đoán</h6>
            """, unsafe_allow_html=True)
        st.write(f'Mean Squared Error on test set: {mse_optimized_xgb}')
        st.write(f'Root Mean Squared Error on test set: {rmse_optimized_xgb}')
        st.write(f'R-squared (Coefficient of Determination) on test set: {r_squared_optimized_xgb}')
    with st.container():
        # Vẽ biểu đồ line
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=list(range(len(y_test))), y=y_test, mode='lines', name='Giá trị thực tế', line=dict(color='blue')))
        fig1.add_trace(go.Scatter(x=list(range(len(y_test))), y=y_pred_optimized_xgb, mode='lines', name='Giá trị dự đoán', line=dict(color='red')))
        fig1.update_layout(title='Giá trị dự đoán và giá trị thực tế của doanh thu', xaxis_title='Số thứ tự', yaxis_title='Doanh thu')
        st.plotly_chart(fig1)
        
        col1, col2 = st.columns(2)
    with col1:
        fig2 = px.histogram(x=y_test - y_pred_optimized_xgb, nbins=20, title='Distribution of Residuals')
        fig2.add_vline(x=0, line=dict(color='red', dash='dash', width=2), name='Zero Residual Line')
        fig2.update_layout(xaxis_title='Residuals (Actual - Predicted)', yaxis_title='Frequency')
        st.plotly_chart(fig2)

    with col2:
        fig3 = px.scatter(x=y_test, y=y_pred_optimized_xgb, title='Scatter Plot between Actual and Predicted Sales', opacity=0.5)
        fig3.add_trace(go.Scatter(x=[min(y_test), max(y_test)], y=[min(y_test), max(y_test)], mode='lines', line=dict(color='red', dash='dash'), name='Perfect Prediction'))
        fig3.update_layout(xaxis_title='Actual Total Sales', yaxis_title='Predicted Total Sales')
        st.plotly_chart(fig3)
    
    return model_xgb


def Model(original_path):
    st.title("Mô Hình Dự Báo Doanh Thu")        
    # # Upload file
    uploaded_file = st.file_uploader("Upload a file", type=["xlsx", "csv"], key="model")
    if uploaded_file is not None:
        # Cập nhật dữ liệu tổng hợp
        df_combined = load_all_data(uploaded_file)

        # Hiển thị dashboard tổng quan
        file_model = buid_model(df_combined)
        
        if st.button("Update mô hình - dữ liệu vào hệ thống"):
            # Xóa file cũ trong thư mục ./src/model
            model_dir = './model'
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            for filename in os.listdir(model_dir):
                file_path = os.path.join(model_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    st.write(f'Failed to delete {file_path}. Reason: {e}')
            
            # Lưu mô hình vào thư mục ./src/model
            model_path = os.path.join(model_dir, 'model_xgb.pkl')
            shutil.move(file_model, model_path)
            
            # Tải dữ liệu lên MySQL
            df_combined.to_sql('adidas_4', con=engine, if_exists='replace', index=False)
            st.write("Dữ liệu đã được cập nhật lên MySQL")
