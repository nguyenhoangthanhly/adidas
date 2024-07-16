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
import src.Predict.Forcasting as forcasting 
import src.Predict.Model as modelxgb 

warnings.filterwarnings('ignore')

def Predict(original_path):
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=["EDA", "Mô Hình","Dự Đoán"],
            # icons=["house", "eye"],
            menu_icon="cast",
            default_index=0
        )
    if selected == "EDA":
        dataCleaning.DataCleaning()
    if selected == "Mô Hình":
        modelxgb.Model(original_path)
    if selected == "Dự Đoán":
        forcasting.Forcasting(original_path)