import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
import os

from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
import src.query as query

def Product():
    with st.container(border = True):
        fl = st.file_uploader(":file_folder: Upload a file",type=(["xlsx", "csv"]))
    if fl is not None:
        file_name = fl.name
        _, file_extension = os.path.splitext(file_name)
        if file_extension == '.xlsx':
            df = pd.read_excel(fl)
        elif file_extension == '.csv':
            df = pd.read_csv(fl)
        else:
            st.write(f"{file_name} không phải là file Excel (.xlsx) hoặc CSV (.csv)")
    else:
        result = query.view_all_data()
        df = pd.DataFrame(result, columns=["Retailer", "Region", "State", "City", "Product", "Price per Unit", "Units Sold", "Operating Profit", "Sales Method", "Total Sales", "Month", "Year", "Day", "Season", "Date", "id"])
    with st.container(border=True):
        col_year, col_region, col_state = st.columns(3)
        col_city, col_retailer = st.columns(2)
        with col_year:
            # Create for year
            year = st.multiselect("Pick your Year", df["Year"].unique())
            if not year:
                df2 = df.copy()
            else:
                df2 = df[df["Year"].isin(year)]
        with col_region:
            region = st.multiselect("Pick your Region", df2["Region"].unique())
            if not region:
                df3 = df2.copy()
            else:
                df3 = df2[df2["Region"].isin(region)]
        with col_state:
            state = st.multiselect("Pick the State", df3["State"].unique())
            if not state:
                df4 = df3.copy()
            else:
                df4 = df3[df3["State"].isin(state)]
        with col_city:
            city = st.multiselect("Pick the City",df4["City"].unique())
            if not city:
                df5 = df4.copy()
            else:
                df5 = df4[df4["City"].isin(city)]
        with col_retailer:
            retailer = st.multiselect("Pick your Retailer", df4["Retailer"].unique())
            if not retailer:
                df5 = df4.copy()
            else:
                df5 = df4[df4['Retailer'].isin(retailer)]
    st.subheader(f"Detail - Sản Phẩm")
    col1, col2, col3 = st.columns((3))
    df5["Date"] = pd.to_datetime(df5["Date"])

    # Getting the min and max date 
    startDate = pd.to_datetime(df5["Date"]).min()
    endDate = pd.to_datetime(df5["Date"]).max()

    with col3:
        with st.container(border=True):
            date1 = pd.to_datetime(st.date_input("Start Date", startDate))

        with st.container(border=True):
            date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df5 = df5[(df5["Date"] >= date1) & (df5["Date"] <= date2)].copy()
    
    total_product = float(pd.Series(df5['Units Sold']).sum())
    total_transactions = float(df5.shape[0])
    with col1:
        with st.container(border=True):
            # Toongr doanh thu
            st.info('Total Amount Product',icon="💰")
            st.metric(label="",value=f"{total_product:,.0f}")
    with col2:
        with st.container(border=True):
            st.info('Total Transactions', icon="💰")
            st.metric(label="", value=f"{total_transactions:,.0f}")
    style_metric_cards(background_color="#FFFFFF",border_left_color="#1E90FF",border_color="#000000",box_shadow="#1E90FF")

    col4, col5 = st.columns((2))
    with col4:
        with st.container(border = True):
            amount_product = df5.groupby('Product')['Units Sold'].sum().reset_index()
            fig4_product = go.Figure()
            fig4_product.add_trace(go.Bar(
                y=amount_product['Units Sold'],
                x=amount_product['Product'],
                name='Tổng sản lượng',
                # orientation='h',
                marker=dict(color='#FF9EAA'),
                text=amount_product['Units Sold'].apply(lambda x: f'{x:.2f}'),
                textposition='inside',
                insidetextanchor='middle',
                hovertemplate='%{x}<br>%{text}'
            ))
        
            fig4_product.update_layout(
                title='Số Lượng Bán Ra Từng Sản Phẩm',
                barmode='group',
                xaxis_title='Sản phẩm',
                yaxis_title='Số lượng',
                legend_title='Chỉ Số',
                margin=dict(t=30,r=5,l=5,b=5)
            )
            st.plotly_chart(fig4_product, use_container_width=True)  
    with col5:
        with st.container(border=True):
            method_product = df5.groupby(['Year','Season'])['Units Sold'].sum().reset_index()
            # Tạo nhãn cho trục x
            method_product['Label'] = method_product.apply(lambda row: f"Năm {row['Year']} - Quý {row['Season']}", axis=1)

            # Tính tốc độ tăng trưởng doanh thu theo từng quý trong năm
            method_product['Growth Rate'] = method_product['Units Sold'].pct_change() * 100
            # quarter_data['Profit Growth Rate'] = quarter_data['Operating Profit'].pct_change() * 100

            fig_time2 = go.Figure()
            fig_time2.add_trace(go.Bar(
                y=method_product['Units Sold'],
                yaxis='y',
                x=method_product['Label'],
                name='Số lượng',
                # orientation='v',
                marker=dict(color='#1E90FF'),
                text=method_product['Units Sold'],
                textposition='inside',
                insidetextanchor='middle',
                #hovertemplate='Doanh Thu: %{x}<br>%{text}'
            ))
            fig_time2.add_trace(go.Scatter(
                x=method_product['Label'],
                y=method_product['Growth Rate'],
                yaxis='y2',
                mode='lines+markers',
                name='TĐTT Số lượng',
                line=dict(color='#FF0000'),
                text=method_product['Growth Rate'],
                #textposition='center'
            ))
            fig_time2.update_layout(
                title='Số Lượng Bán Ra Qua Từng Năm',
                xaxis_title='Quý',
                yaxis=dict(
                    title='Giá Trị',
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue'),
                    showgrid=False
                ),
                yaxis2=dict(
                    title='Growth Rate (%)',
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red'),
                    overlaying='y',
                    side='right',
                    # range=[100,300],
                    showgrid=False
                ),
                legend_title=dict(text='Chỉ Số'),
                barmode='group',
                margin=dict(t=30,r=5,l=5,b=5)
            )

            st.plotly_chart(fig_time2, use_container_width=True) 
    
    col6, col7 = st.columns([6,4])
    with col6:
        with st.container(border = True):
            retailer_product = df5.groupby(['Retailer','Region'])['Units Sold'].sum().reset_index()
            fig6 = go.Figure()
            regions = retailer_product['Region'].unique()
            # colors = px.colors.qualitative.Plotly  # Sử dụng bảng màu mặc định của Plotly
            colors = {
                'West': '#1f77b4',
                'Northeast': '#aec7e8',
                'Southeast': '#ff7f0e',
                'South': '#ffbb78',
                'Midwest': '#2ca02c'
            }
            for i, region in enumerate(regions):
                region_data = retailer_product[retailer_product['Region'] == region]
                fig6.add_trace(go.Bar(
                    y=region_data['Retailer'],
                    x=region_data['Units Sold'],
                    name=region,
                    orientation='h',
                    marker=dict(color=colors[region]),
                    # text=region_data['Units Sold'],
                    textposition='inside',
                    insidetextanchor='middle',
                ))
            fig6.update_layout(
                title='Số Lượng Bán Ra Từng Nhà Bán Lẻ Tại Mỗi Khu Vực',
                barmode='stack',
                yaxis_title='Sản phẩm',
                xaxis_title='Số lượng',
                # legend_title='Region',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.3
                ),
                margin=dict(t=30,r=5,l=5,b=5),
                bargap=0.75
            )
            st.plotly_chart(fig6, use_container_width=True)  

    with col7:
        with st.container(border=True):
            sales_methd_product = df5.groupby('Sales Method')['Units Sold'].sum().reset_index()
            fig7 = go.Figure()
            fig7.add_trace(go.Pie(
                labels=sales_methd_product['Sales Method'],
                values=sales_methd_product['Units Sold'],
                name="Tổng số lượng",
                # hole=0.7,
                domain={'x': [0, 1], 'y': [0, 1]},
                textinfo='percent',
                textposition='inside',
                insidetextorientation='radial',
                # marker=dict(colors=list(colors_profit.values())
                #             ),
                hoverinfo='label+percent+name',
                hovertemplate='%{label}<br>Percentage: %{percent}<br>Value: %{value}<extra></extra>'
            ))
            fig7.update_layout(
                title='Số Lượng Bán Ra Theo Phương Pháp Bán Hàng',
                showlegend=True,
                # legend=dict(
                #     orientation="h",
                #     yanchor="bottom",
                #     y=-0.3,
                #     xanchor="center",
                #     x=0.5
                # ),
                margin=dict(t=30,r=5,l=5,b=5),
                height=200
            )
            st.plotly_chart(fig7, use_container_width=True)
        with st.container(border=True, height=250):
            st.markdown("""
                <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Gía Bán Trung Bình Trừng Sản Phẩm</h6>
                """, unsafe_allow_html=True)
            # Tính giá bán trung bình theo từng sản phẩm
            average_price_per_product = df5.groupby('Product')['Price per Unit'].mean().reset_index()
            # Sắp xếp sản phẩm theo giá bán trung bình giảm dần
            average_price_per_product = average_price_per_product.sort_values(by='Price per Unit', ascending=False)
            st.dataframe(average_price_per_product)
    
    with st.container(border=True):
        col8, col9 = st.columns((2))
        # product = st.multiselect("Pick your Product", df5["Product"].unique())
        # if not year:
        #     df6 = df5.copy()
        # else:
        #     df6 = df5[df5["Product"].isin(product)]
        colors = {
            "Men's Street Footwear": '#B1AFFF',
            "Women's Apparel":'#BBE9FF',
            "Men's Athletic Footwear":'#FFFED3',
            "Women's Street Footwear":'#FFE9D0',
            "Men's Apparel":'#ffbb78',
            "Women's Athletic Footwear":'#2ca02c'
        }
        with col8:
            with st.container(border=True):
                price_product_by_method = df5.groupby(['Sales Method','Product'])['Price per Unit'].mean().reset_index()
                fig8 = go.Figure()
                product_unique = price_product_by_method['Product'].unique()
                for i, products in enumerate(product_unique):
                    product_data = price_product_by_method[price_product_by_method['Product'] == products]
                    fig8.add_trace(go.Bar(
                        y=product_data['Sales Method'],
                        x=product_data['Price per Unit'],
                        name=products,
                        orientation='h',
                        marker=dict(color=colors[products]),
                        # text=region_data['Units Sold'],
                        textposition='inside',
                        insidetextanchor='middle',
                    ))
                fig8.update_layout(
                    title='Giá Bán Trung Bình Mỗi Sản Phẩm Theo Từng Phương Pháp Bán Hàng',
                    # barmode='stack',
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(t=30,r=5,l=5,b=5,),
                    bargap=0.5
                )
            st.plotly_chart(fig8, use_container_width=True)
        with col9:
            with st.container(border=True):
                price_product_by_region = df5.groupby(['Region','Product'])['Price per Unit'].mean().reset_index()
                fig9 = go.Figure()
                product_unique = price_product_by_region['Product'].unique()
                for i, products in enumerate(product_unique):
                    product_data = price_product_by_region[price_product_by_region['Product'] == products]
                    fig9.add_trace(go.Bar(
                        x=product_data['Region'],
                        y=product_data['Price per Unit'],
                        name=products,
                        orientation='v',
                        marker=dict(color=colors[products]),
                        # text=region_data['Units Sold'],
                        textposition='inside',
                        insidetextanchor='middle',
                    ))
                fig9.update_layout(
                title='Giá Bán Trung Bình Mỗi Sản Phẩm Tại Từng Khu Vực',
                # barmode='stack',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(t=30,r=5,l=5,b=5,),
                bargap=0.5
            )
            st.plotly_chart(fig9, use_container_width=True)



    