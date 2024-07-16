import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import datetime as dt
import plotly.graph_objects as go
import pandas as pd
import pandas.io.formats.style
import folium
from streamlit_folium import st_folium
import pygwalker as pyg
import requests
import os
import io 
import sys
from pygwalker.api.streamlit import StreamlitRenderer
import warnings
from streamlit_option_menu import option_menu
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import joblib
import time
from xgboost.sklearn import XGBRegressor
from io import StringIO
from src.mapData import get_region_mapping, get_state_mapping, get_city_mapping, get_product_mapping, get_sales_method_mapping, get_retailer_mapping, prepare_data

warnings.filterwarnings('ignore')
def load_data(file):
    # Hiển thị thanh tiến trình tùy chỉnh
    progress_bar = st.progress(0, text="Operation in progress. Please wait.")
    file_name = file.name
    _, file_extension = os.path.splitext(file_name)
    if file_extension == '.xlsx':
        df = pd.read_excel(file)
    elif file_extension == '.csv':
        df = pd.read_csv(file)
    # df = pd.read_excel(file)
    for percent_complete in range(100):
        time.sleep(0.01)  # Giả lập thời gian xử lý
        progress_bar.progress(percent_complete + 1, text="Operation in progress. Please wait.")
    return df

# Hàm để hiển thị tổng quan dữ liệu
def display_data_overview(df):
    if df is not None:
        with st.container(border=True, height=300):
            st.markdown("""
                <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Tổng Quan Dữ Liệu</h6>
                """, unsafe_allow_html=True)
            st.write(f"Số dòng: {df.shape[0]}")
            st.write(f"Số thuộc tính: {df.shape[1]}")
            st.dataframe(df)
        col1, col2 = st.columns([4, 6])
        with col1:
            with st.container(border=True):
                data_types_df = pd.DataFrame({
                    'Tên thuộc tính': df.columns,
                    'Kiểu dữ liệu': df.dtypes.values
                })
                st.markdown("""
                <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Kiểu Dữ Liệu Thuộc Tính</h6>
                """, unsafe_allow_html=True)
                st.dataframe(data_types_df, height=300, width=500)
        with col2:
            with st.container(border=True):    
                duplicate_rows = df.duplicated(keep="first").sum()
                st.write(f"Số lượng dòng trùng lặp: {duplicate_rows}")
            with st.container(border=True, height=300):
                    missing_data_percentage = 100 * df.isnull().sum().sort_values(ascending=False) / len(df)
                    missing_data_percentage_df = pd.DataFrame({
                        'Tên thuộc tính': missing_data_percentage.index,
                        'Phần trăm dữ liệu bị thiếu': missing_data_percentage.values
                    })
                    st.markdown("""
                    <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Phần Trăm Dữ Liệu Bị Thiếu</h6>
                    """, unsafe_allow_html=True)
                    st.dataframe(missing_data_percentage_df, height=300, width=700)

def handle_duplicates(df):
    return df.drop_duplicates()

def handle_missing_data(df, column, method):
    if df[column].dtype == 'object':
        if method == "Delete":
            return df.dropna(subset=[column])
        elif method == "Fill with mode":
            return df.fillna({column: df[column].mode()[0]})
    else:
        if method == "Delete":
            return df.dropna(subset=[column])
        elif method == "Fill with mean":
            return df.fillna({column: df[column].mean()})
    return df

# Hàm để hiển thị phân phối dữ liệu
def display_distributions(df):
    if df is not None:
        st.markdown("""
            <h3 style="font-size: 25px; font-weight: bold;">Distribution Categorical</h3>
            """, unsafe_allow_html=True)
        with st.expander("Xem Kết Quả"):
            with st.container(border=True):
                categorical_attributes = df.select_dtypes(include=['object']).columns
                for attr in categorical_attributes:
                    fig = px.histogram(df, x=attr, color_discrete_sequence=['#FFA07A'])
                    fig.update_layout(title=f'Distribution of {attr}', xaxis_title=attr, yaxis_title='Count')
                    st.plotly_chart(fig)
        
        st.markdown("""
            <h3 style="font-size: 25px; font-weight: bold;">Distribution Continous</h3>
            """, unsafe_allow_html=True)
        with st.expander("Xem Kết Quả"):
            with st.container(border=True):
                st.dataframe(df.describe(), width=1000)
                numerical_attributes = df.select_dtypes(include=['number']).columns
                for attr in numerical_attributes:
                    # Drop NaN values for the current attribute
                    valid_data = df[attr].dropna()

                    if not valid_data.empty:
                        fig = px.histogram(valid_data, x=attr, nbins=10, marginal='violin', color_discrete_sequence=['#FFA07A'])
                        fig.update_layout(
                            title=f'Distribution of {attr}',
                            xaxis_title=attr,
                            yaxis_title='Frequency'
                        )
                        st.plotly_chart(fig)
def load_result(df, changed_columns):
    if df is not None:
        with st.container(border=True):
            st.markdown("""
                <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Tổng Quan Dữ Liệu</h6>
                """, unsafe_allow_html=True)
           
            col1, col2 = st.columns([4, 6])
            with col1:
                with st.container(border=True):
                    data_types_df = pd.DataFrame({
                                        'Tên thuộc tính': st.session_state.df.columns,
                                        'Kiểu dữ liệu': st.session_state.df.dtypes.values,
                                        'Đã chuyển đổi': ['Có' if col in changed_columns else 'Không' for col in st.session_state.df.columns]
                                    })
                                    
                    st.markdown("""
                    <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Kiểu Dữ Liệu Thuộc Tính</h6>
                    """, unsafe_allow_html=True)
                    
                    def highlight_changed(s):
                        is_changed = s['Đã chuyển đổi'] == 'Có'
                        return ['background-color: yellow' if is_changed else '' for v in s]
                    
                    styled_df = data_types_df.style.apply(highlight_changed, axis=1)
                    st.dataframe(styled_df, width=700)
            with col2:
                with st.container(border=True):    
                    duplicate_rows = df.duplicated(keep="first").sum()
                    st.write(f"Số lượng dòng trùng lặp: {duplicate_rows}")
                    st.write(f"Số dòng: {df.shape[0]}")
                    st.write(f"Số thuộc tính: {df.shape[1]}")
                with st.container(border=True, height=300):
                        missing_data_percentage = 100 * df.isnull().sum().sort_values(ascending=False) / len(df)
                        missing_data_percentage_df = pd.DataFrame({
                            'Tên thuộc tính': missing_data_percentage.index,
                            'Phần trăm dữ liệu bị thiếu': missing_data_percentage.values
                        })
                        st.markdown("""
                        <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Phần Trăm Dữ Liệu Bị Thiếu</h6>
                        """, unsafe_allow_html=True)
                        st.dataframe(missing_data_percentage_df, height=300, width=700)
def DataCleaning():
    changed_column = []

    # Khởi tạo session state nếu chưa có
    if "df" not in st.session_state:
        st.session_state.df = None
    if 'uploaded_filename' not in st.session_state:
        st.session_state.uploaded_filename = None
    if "init_flag" not in st.session_state:
        st.session_state.init_flag = False

    # File upload and data processing
    
    fl = st.file_uploader("Upload a file", type=["xlsx", "csv"], key="fileuploader")
    if fl:     
        if st.session_state.uploaded_filename != fl.name:
            st.session_state.df = load_data(fl)
            st.session_state.uploaded_filename = fl.name
            st.session_state.init_flag = True
    st.title("1. DataSet")
    display_data_overview(st.session_state.df)
    if st.session_state.df is not None:
        st.title("2. Xử Lý Dữ Liệu")

        # Xử lý dữ liệu bị thiếu
        st.header("Xử Lý Dữ Liệu Bị Thiếu")
        missing_columns = st.session_state.df.columns[st.session_state.df.isnull().any()].tolist()
        if missing_columns:
            # Kiểm tra kiểu dữ liệu của cột được chọn
            # Check data type of selected column
            column = st.selectbox("Chọn thuộc tính bị thiếu", missing_columns)
            if st.session_state.df[column].dtype == 'object':
                method_options = ['Delete', 'Fill with mode']
            else:
                method_options = ['Delete', 'Fill with mean']

            method = st.selectbox("Chọn phương pháp xử lý", method_options)
            if st.button("Xử lý dữ liệu bị thiếu"):
                st.session_state.df = handle_missing_data(st.session_state.df, column, method)
                st.success(f"Đã xử lý dữ liệu bị thiếu cho thuộc tính {column}", icon="✅")
                with st.expander("Xem kết quả"):
                    missing_data_percentage = 100 * st.session_state.df.isnull().sum().sort_values(ascending=False) / len(st.session_state.df)
                    missing_data_percentage_df = pd.DataFrame({
                        'Tên thuộc tính': missing_data_percentage.index,
                        'Phần trăm dữ liệu bị thiếu': missing_data_percentage.values
                    })
                    st.dataframe(missing_data_percentage_df, height=300, width=700)
        else:
            st.write("Không có thuộc tính nào bị thiếu dữ liệu")

        # Xử lý dòng dữ liệu trùng lặp
        st.header("Xử Lý Dòng Dữ Liệu Trùng Lặp")
        if st.button("Xử Lý Dòng Dữ Liệu Trùng Lặp", type="primary", key="Duplicate"):
            st.session_state.df = handle_duplicates(st.session_state.df)
            st.success(f"Số Dòng Trùng Lặp: {st.session_state.df.duplicated(keep=False).sum()}", icon="✅")

        # Chuẩn hóa kiểu dữ liệu
        st.header("Chuẩn Hóa Kiểu Dữ Liệu")
        if st.button("Chuẩn Hóa Kiểu Dữ Liệu", type="primary", key="Transform"):
            dtype_mapping = {
                'Region': 'object',
                'State': 'object',
                'City': 'object',
                'Retailer': 'object',
                'Product': 'object',
                'Sales Method': 'object',
                'Units Sold': 'int64',
                'Total Sales': 'float64',
                'Operating Profit': 'float64',
                'Price per Unit': 'float64'
            }

            initial_dtypes = st.session_state.df.dtypes.copy()  
            st.session_state.df = st.session_state.df.astype(dtype_mapping)
            st.success('Chuẩn Hóa Kiểu Dữ Liệu Thành Công', icon="✅")
            # Identify changed columns
            changed_columns = initial_dtypes[initial_dtypes != st.session_state.df.dtypes].index.tolist()
            changed_column = changed_columns

        load_result(st.session_state.df, changed_column)
        st.title("3. Distribution")
        display_distributions(st.session_state.df)
        st.title("4. Chart")
        with st.expander("Click"):
            pyg_app = StreamlitRenderer(st.session_state.df)
            pyg_app.explorer()

        st.session_state.df['Date'] = pd.to_datetime(st.session_state.df['Date'])
        st.session_state.df['Month'] = st.session_state.df['Date'].dt.month
        st.session_state.df['Year'] = st.session_state.df['Date'].dt.year
        st.session_state.df['Day'] = st.session_state.df['Date'].dt.day
        def find_seasons(monthNumber):
            if monthNumber in [1, 2, 3]:
                return 'Q1'

            elif monthNumber in [4, 5, 6]:
                return 'Q2'

            elif monthNumber in [7, 8 ,9]:
                return 'Q3'

            elif monthNumber in [10, 11, 12]:
                return 'Q4'

        st.session_state.df['Season'] = st.session_state.df['Month'].apply(find_seasons)
        st.session_state.df = st.session_state.df[['Retailer', 'Region', 'State', 'City', 'Product', 'Price per Unit', 'Units Sold', 'Operating Profit','Sales Method', 'Total Sales', 'Month', 'Year', 'Day', 'Date']]
        # Button to export the processed DataFrame to an Excel file
        if st.button("Xuất file Excel"):
            output = io.StringIO()
            st.session_state.df.to_csv(output, index=False)
            
            output.seek(0)
            st.download_button(
                label="Tải xuống file CSV đã xử lý",
                data=output.getvalue(),
                file_name=f"{st.session_state.uploaded_filename}",
                mime="text/csv"
            )