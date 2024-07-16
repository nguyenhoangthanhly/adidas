import sys
import os
import streamlit as st
original_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
current_path = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_path, '..'))
os.chdir(src_path)
sys.path.append(src_path)
import pandas as pd
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import requests
import warnings
import src.query as query
import src.Dashboard.OverView as ov 
import src.Dashboard.Project as prj 
import src.Dashboard.Predict as prd

warnings.filterwarnings('ignore')


st.set_page_config(page_title="Dashboard - Adidas", page_icon="", layout="wide")
result = query.view_all_data()
df = pd.DataFrame(result, columns=["Retailer", "Region", "State", "City", "Product", "Price per Unit", "Units Sold", "Operating Profit", "Sales Method", "Total Sales", "Month", "Year", "Day", "Season", "Date", "id"])

st.markdown('<style>div.block-container{padding-top:3rem;}</style>',unsafe_allow_html=True)
st.markdown("""
    <style>
        .st-emotion-cache-r421ms {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px);
            background-color: white;
        }
 
    </style>
    """, unsafe_allow_html=True)

# horizontal menu
with st.container(border=True):
    selected = option_menu(
        menu_title="DASHBOARD ADIDAS",
        options=["OverView","Detail","Predict"],
        # icons=["house", "book", "envelope"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "border-radius": "10px",  
                "display": "flex",  
                "justify-content": "space-around",  
            },
            "icon": {
                "color": "", 
                "font-size": "25px",
            },
            "nav-link": {
                "font-size": "25px",
                "text-align": "center",  
                "margin": "0 30px 0 50px",  
                "--hover-color": "#4682B4",  
                "padding": "10px 20px",  
                "color": "black",  
                "background-color": "#B0DAFF",  
                "border-radius": "8px",  
                "width": "250px" 
            },
            "nav-link-selected": {
                "background-color": "#5AB2FF",  
                "color": "white",  
            },
            "nav-item":{
                "display": "flex",
                "align-items":"center"
            }
        },
    )


if selected == "OverView":
    ov.OverView(original_path)
if selected == "Detail":
    prj.Project(original_path)
if selected == "Predict":
    prd.Predict(original_path)
