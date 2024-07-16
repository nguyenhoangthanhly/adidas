import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards

import src.Detail.Product as product 
import src.Detail.Profit as profit 
import src.Detail.TotalSalse as totalSalse 

def Project(original_path):
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=["Doanh Thu", "Lợi Nhuận", "Sản Phẩm"],
            icons=["house", "eye"],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Doanh Thu":
        totalSalse.TotalSalse(original_path)
    if selected == "Lợi Nhuận":
        profit.Profit(original_path)
    if selected == "Sản Phẩm":
        product.Product()