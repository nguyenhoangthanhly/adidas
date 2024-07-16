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
from pygwalker.api.streamlit import StreamlitRenderer
import warnings
from streamlit_option_menu import option_menu
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import joblib
from xgboost.sklearn import XGBRegressor

from src.mapData import get_region_mapping, get_state_mapping, get_city_mapping, get_product_mapping, get_sales_method_mapping, get_retailer_mapping, prepare_data
import src.Predict.DataCleaning as dataCleaning 
import src.query as query

warnings.filterwarnings('ignore')
def Forcasting(original_path):
    st.title('Total Sales Forcasting')
    # data_predict đã tạo dữ liệu dữ liệu dự đoán và chuẩn hóa 
    data_predict = os.path.join(original_path, 'data\external', 'data_predict.csv')
    df_predict = pd.read_csv(data_predict)

    # data_draw đã tạo dữ liệu dùng để vẽ biểu đồ
    data_draw = os.path.join(original_path, 'data\external', 'data_draw.csv')
    df_draw = pd.read_csv(data_draw)

    # data là file tổng hợp doanh số bán hàng các năm 
    result = query.view_all_data()
    df = pd.DataFrame(result, columns=["Retailer", "Region", "State", "City", "Product", "Price per Unit", "Units Sold", "Operating Profit", "Sales Method", "Total Sales", "Month", "Year", "Day", "Season", "Date", "id"])

    # Tải mô hình dự đoán từ file 
    model = os.path.join(original_path, 'model', 'model_xgb.pkl')
    model_xgb = joblib.load(model)

    # Dự đoán doanh thu sử dụng mô hình đã tải
    predict_xgb = model_xgb.predict(df_predict)
    # Chuyển đổi ngược lại
    y_pred_optimized_xgb = np.expm1(predict_xgb)

    df_draw['Total Sales'] = y_pred_optimized_xgb
    df_draw['Year'] = 2022

    # Thêm cột để phân biệt dữ liệu ban đầu và dự đoán
    df['Source'] = 'Original'
    df_draw['Source'] = 'Predicted'

    sales_by_month = df.groupby(["Year", "Month"])['Total Sales'].sum().reset_index()
    sales_by_month['Source'] = 'Original'

    sales_by_month_predict = df_draw.groupby(["Year", "Month"])['Total Sales'].sum().reset_index()
    sales_by_month_predict['Source'] = 'Predicted'

    merged_df = pd.concat([sales_by_month, sales_by_month_predict], axis=0)
    merged_df['Label'] = merged_df.apply(lambda row: f"{row['Year']}-{row['Month']}", axis=1)
    
    fig_time = go.Figure()
    # Vẽ đường dữ liệu ban đầu
    fig_time.add_trace(go.Scatter(
        x=merged_df['Label'],
        y=merged_df['Total Sales'],
        mode='lines',
        name='Doanh Thu (Dữ liệu ban đầu)',
        line=dict(color='blue')
    ))

    # Vẽ đường dữ liệu dự đoán
    fig_time.add_trace(go.Scatter(
        x=merged_df[merged_df['Source'] == 'Predicted']['Label'],
        y=merged_df[merged_df['Source'] == 'Predicted']['Total Sales'],
        mode='lines',
        name='Doanh Thu (Dữ liệu dự đoán)',
        line=dict(color='red')
    ))

    fig_time.update_layout(
        # title='Doanh Thu Theo Thời Gian',
        xaxis_title='Thời Gian',
        yaxis_title='Giá Trị',
        legend_title='Chỉ Số',
        margin=dict(t=30, r=5, l=5, b=5),
    )

    # Chỉ hiển thị đầu tháng và giữa tháng trên trục x
    fig_time.update_xaxes(
        tickvals=[f"{year}-{month:02d}" for year in range(merged_df['Year'].min(), merged_df['Year'].max() + 1) for month in range(1, 13, 5)]
    )

    st.plotly_chart(fig_time, use_container_width=True)
    total_sales_predict = float(pd.Series(df_draw['Total Sales']).sum())
    col1, col2 = st.columns([3,7])
    with col1:
        # Toongr doanh thu
        with st.container(border=True):
            st.info('Total Sales Predict',icon="💰")
            st.metric(label="",value=f"{total_sales_predict:,.0f}")
        with st.container(border=True, height=200):
            sales_by_year = merged_df.groupby('Year')['Total Sales'].sum().reset_index()
            if len(sales_by_year) >= 2:
                current_year_sales = sales_by_year.iloc[-1]['Total Sales']
                previous_year_sales = sales_by_year.iloc[-2]['Total Sales']
                growth_percentage = ((current_year_sales - previous_year_sales) / previous_year_sales) * 100
            else:
                growth_percentage = 0
            # Biểu đồ chỉ báo phần trăm tăng trưởng
            fig_gauge = go.Figure()
            fig_gauge.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=current_year_sales,
                delta={'reference': previous_year_sales, 'relative': True},
                gauge={
                    'axis': {'visible': False}},
                domain={'x': [0.1, 0.9], 'y': [0.1, 0.9]}
            ))
            fig_gauge.update_layout(
                margin=dict(t=30,r=5,l=5,b=5), 
                title='Tốc Độ Tăng Trưởng Doanh Thu Dự Báo',
                height=200,
                width=300,
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
    with col2:
        col2_1, col2_2 = st.columns([5,5])
        with col2_1:
            with st.container(border=True):
                sales_by_region = df_draw.groupby('Region')['Total Sales'].sum().reset_index()
                fig = px.pie(sales_by_region, values = "Total Sales", names = "Region", hole=0.64)
                fig.update_traces(text = sales_by_region["Region"], textposition = "inside")
                fig.update_layout(margin=dict(t=30,r=5,l=5,b=5), 
                    title='Vùng Có Doanh Thu Dự Báo Cao Nhất',
                    legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                    ),
                )
                st.plotly_chart(fig,use_container_width=True)
        with col2_2:
            with st.container(border=True):
                #Sản phẩm doanh thu cao nhất
                sales_by_product = df_draw.groupby('Product')[['Total Sales']].sum().reset_index().sort_values(by="Total Sales", ascending=True)
                sales_by_product['Sales %'] = (sales_by_product['Total Sales'] / total_sales_predict) * 100
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=sales_by_product['Product'],
                    x=sales_by_product['Total Sales'],
                    name='Doanh Thu',
                    orientation='h',
                    marker=dict(color='#FF9EAA'),
                    text=sales_by_product['Sales %'].apply(lambda x: f'{x:.2f}%'),
                    textposition='inside',
                    insidetextanchor='middle',
                    hovertemplate='Doanh Thu: %{x}<br>%{text}'
                ))
        
                fig.update_layout(
                    title='Sản Phẩm Có Doanh Thu Cao Nhất',
                    barmode='group',
                    xaxis_title='Giá Trị',
                    yaxis_title='Sản Phẩm',
                    legend_title='Chỉ Số',
                    margin=dict(t=30,r=5,l=5,b=5)
                )
                st.plotly_chart(fig, use_container_width=True)  
    with st.container(border=True):
        st.markdown("""
                <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Số Lượng Sản Phẩm Dự Báo Bán Được</h6>
                """, unsafe_allow_html=True)
        col_sliders, col_table = st.columns([6, 4])
        product_prices = {}
        with col_sliders:
            for product in sales_by_product['Product']:
                product_prices[product] = st.slider(f'Giá Trung Bình của {product}', 0, 100, 10, step=10)

        # Calculate and display predicted quantity sold
        sales_by_product['Predicted Quantity'] = sales_by_product.apply(lambda row: row['Total Sales'] / product_prices[row['Product']], axis=1)
        with col_table:
            st.dataframe(sales_by_product[['Product', 'Predicted Quantity']])
    st.title("Dự Báo Doanh Thu Từng Khu Vực")
    with st.container(border=True):
        col_region, col_state = st.columns(2)
        col_city, col_retailer = st.columns(2)
        with col_region:
            region = st.selectbox("Pick your Region", df["Region"].unique(),index=None)
            if not region:
                df3 = df.copy()
            else:
                df3 = df[df["Region"] == region]
        with col_state:
            state = st.selectbox("Pick the State", df3["State"].unique(), index=None)
            if not state:
                df4 = df3.copy()
            else:
                df4 = df3[df3["State"] == state]
        with col_city:
            city = st.selectbox("Pick the City",df4["City"].unique(),index=None)
            if not city:
                df5 = df4.copy()
            else:
                df5 = df4[df4["City"] == city]
        with col_retailer:
            retailer = st.selectbox("Pick your Retailer", df4["Retailer"].unique(),index=None)
            if not retailer:
                df6 = df5.copy()
            else:
                df6 = df5[df5['Retailer'] == retailer]
    selected_product = df['Product'].unique().tolist()
    selected_sales_method = df["Sales Method"].unique().tolist()
    if st.button("Dự Đoán Doanh Thu", type="primary", key="PredictDetail"):
        if not region or not state or not city or not selected_product:
            st.error('Chọn đầy đủ dữ liệu')
        else:
            data_detail = []
            for p in selected_product:
                for sm in selected_sales_method:
                    for m in range(1, 13):
                        data_detail.append([retailer, region, state, city, p, sm, m])

            data_predict_detail = pd.DataFrame(data_detail, columns=["Retailer", "Region", "State", "City", "Product", "Sales Method", "Month"])
            data_draw_detail = pd.DataFrame(data_detail, columns=["Retailer", "Region", "State", "City", "Product", "Sales Method", "Month"])

            region_mapping = get_region_mapping()
            state_mapping = get_state_mapping()
            city_mapping = get_city_mapping()
            product_mapping = get_product_mapping()
            sales_method_mapping = get_sales_method_mapping()
            retailer_mapping = get_retailer_mapping()
            prepared_data_detail = prepare_data(data_predict_detail, region_mapping, state_mapping, city_mapping, product_mapping, retailer_mapping, sales_method_mapping)

            predict_xgb_detail = model_xgb.predict(prepared_data_detail)
            y_pred_optimized_xgb_detail = np.expm1(predict_xgb_detail)

            data_draw_detail['Total Sales'] = y_pred_optimized_xgb_detail
            data_draw_detail['Source'] = 'Predicted'
            data_draw_detail['Year'] = 2022

            sales_by_month_detail = data_draw_detail.groupby(['Year', 'Month'])['Total Sales'].sum().reset_index()
            sales_by_month_detail['Source'] = 'Predicted'

            # Filter original data based on selected values
            df_filtered = df[(df['Region'] == region) &
                                (df['State'] == state) & 
                                (df['City'] == city) & 
                                (df['Retailer'] == retailer)]
            # st.dataframe(df_filtered)
            original_sales_by_month = df_filtered.groupby(['Year', 'Month'])['Total Sales'].sum().reset_index()
            original_sales_by_month['Source'] = 'Original'

            merged_sales_detail = pd.concat([sales_by_month_detail, original_sales_by_month], axis=0)
            merged_sales_detail['Label'] = merged_sales_detail.apply(lambda row: f"{int(row['Year'])}-{int(row['Month']):02d}", axis=1)
            st.dataframe(merged_sales_detail)
            fig_time_detail = go.Figure()
            fig_time_detail.add_trace(go.Scatter(
                x=merged_sales_detail['Label'],
                y=merged_sales_detail['Total Sales'],
                mode='lines',
                name='Doanh Thu (Dữ liệu ban đầu)',
                line=dict(color='blue')
            ))

            fig_time_detail.add_trace(go.Scatter(
                x=merged_sales_detail[merged_sales_detail['Source'] == 'Predicted']['Label'],
                y=merged_sales_detail[merged_sales_detail['Source'] == 'Predicted']['Total Sales'],
                mode='lines',
                name='Doanh Thu (Dữ báo)',
                line=dict(color='red')
            ))

            fig_time_detail.update_layout(
                xaxis_title='Thời Gian',
                yaxis_title='Giá Trị',
                legend_title='Chỉ Số',
                margin=dict(t=30, r=5, l=5, b=5),
            )
            # Chỉ hiển thị đầu tháng và giữa tháng trên trục x
            fig_time.update_xaxes(
                tickvals=[f"{year}-{month:02d}" for year in range(merged_sales_detail['Year'].min(), merged_sales_detail['Year'].max() + 1) for month in range(1, 13, 5)]
            )

            st.plotly_chart(fig_time_detail, use_container_width=True)




