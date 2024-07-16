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

def TotalSalse(original_path):
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
    st.subheader(f"Detail - Doanh Thu")
    col1, col2 = st.columns((2))
    df5["Date"] = pd.to_datetime(df5["Date"])

    # Getting the min and max date 
    startDate = pd.to_datetime(df5["Date"]).min()
    endDate = pd.to_datetime(df5["Date"]).max() 

    with col2:
        with st.container(border=True):
            date1 = pd.to_datetime(st.date_input("Start Date", startDate))

        with st.container(border=True):
            date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df5 = df5[(df5["Date"] >= date1) & (df5["Date"] <= date2)].copy()
    total_sales = float(pd.Series(df5['Total Sales']).sum())
    
    with col1:
        col_sale, col_growth = st.columns(2)
        with col_sale:
            with st.container(border=True):
                # Toongr doanh thu
                st.info('Total Sales',icon="💰")
                st.metric(label="",value=f"{total_sales:,.0f}")
        with col_growth:
            with st.container(border=True):
                sales_by_year = df5.groupby('Year')['Total Sales'].sum().reset_index()
                if len(sales_by_year) >= 2:
                    current_year_sales = sales_by_year.iloc[-1]['Total Sales']
                    previous_year_sales = sales_by_year.iloc[-2]['Total Sales']
                    growth_percentage = ((current_year_sales - previous_year_sales) / previous_year_sales) * 100
                else:
                    year_start = df['Year'].min()  # Năm bắt đầu
                    if len(sales_by_year) == 1:
                        if sales_by_year['Year'].values[0] == year_start:
                            growth_percentage = 0
                            current_year_sales = sales_by_year.iloc[0]['Total Sales']
                            previous_year_sales = 0
                        else:
                            current_year_sales = sales_by_year.iloc[0]['Total Sales']
                            previous_year = sales_by_year['Year'].values[0] - 1
                            sales_by_year_original = df.groupby('Year')['Total Sales'].sum().reset_index()
                            previous_year_sales = sales_by_year_original[sales_by_year_original['Year'] == previous_year]['Total Sales'].values[0] if not sales_by_year_original[sales_by_year_original['Year'] == previous_year].empty else 0
                            if previous_year_sales > 0:
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
                    title='TDTT-DT Năm Hiên Tại / Trước',
                    height=165,
                    width=300,
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

        style_metric_cards(background_color="#FFFFFF",border_left_color="#1E90FF",border_color="#000000",box_shadow="#1E90FF")

    col3, col4 = st.columns((2))
    with col3:
        with st.container(border=True):
            sales_by_region = df5.groupby('Region')['Total Sales'].sum().reset_index()
            fig = px.pie(sales_by_region, values = "Total Sales", names = "Region", hole=0.64)
            fig.update_traces(text = sales_by_region["Region"], textposition = "inside")
            fig.update_layout(margin=dict(t=30,r=5,l=5,b=5), title='Vùng Có Doanh Thu Cao Nhất')
            st.plotly_chart(fig,use_container_width=True)
    with col4:
        with st.container(border=True):
            # Biểu đồ doanh thu theo thời gian
            sales_profit_quarter_data = df.groupby(['Year', 'Month']).agg({
                    'Total Sales': 'sum',
                    'Operating Profit': 'sum'
                }).reset_index()
            # Tạo nhãn cho trục x
            sales_profit_quarter_data['Label'] = sales_profit_quarter_data.apply(lambda row: f"{row['Year']}-{row['Month']}", axis=1)
            fig_time = go.Figure()
            fig_time.add_trace(go.Scatter(
                x=sales_profit_quarter_data['Label'],
                y=sales_profit_quarter_data['Total Sales'],
                mode='lines',
                name='Doanh Thu',
                line=dict(color='#1E90FF')
            ))
            fig_time.update_layout(
                title='Doanh Thu Theo Thời Gian',
                xaxis_title='Thời Gian',
                yaxis_title='Giá Trị',
                legend_title='Chỉ Số',
                margin=dict(t=30,r=5,l=5,b=5)
            )

            st.plotly_chart(fig_time, use_container_width=True)
    
    with st.container(border=True):
        col_map, col_dataframe = st.columns([7, 3])
        with col_map:
            # Bản đồ thế giới thể hiện doanh thu theo từng bang
            us_cities_coordinates = os.path.join(original_path, 'src', 'us_cities_coordinates.xlsx')
            city_sales = df5.groupby("City")["Total Sales"].sum().reset_index()
            df_lat_lon = pd.read_excel(us_cities_coordinates)
            m = folium.Map(location=[38, -96.5], zoom_start=4, scrollWheelZoom=False)
            merged_df = pd.merge(city_sales, df_lat_lon, on="City")
            # Vẽ bubble map ,
            fig = px.scatter_geo(merged_df, lat='latitude', lon='longitude', hover_name='City',
                                size='Total Sales', scope='usa', title="Doanh Thu 52 Thành Phố Tại Mỹ",
                                color='Total Sales', color_continuous_scale=px.colors.cyclical.IceFire)
            fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0},
                geo=dict(
                    scope='usa',
                    landcolor= 'rgb(217, 217, 217)'
                ),
                height=300  
            )
            # fig.update_traces(sizemin=5)
            # Hiển thị trên Streamlit
            st.plotly_chart(fig, use_container_width=True)
        with col_dataframe:
            st.markdown("""
                <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Top 5 Thành Phố Doanh Thu Cao Nhất</h6>
                """, unsafe_allow_html=True)
            revenue_by_city = df5.groupby("City")[["Total Sales"]].sum().reset_index().sort_values(by="Total Sales", ascending=True).head(5)
            st.dataframe(revenue_by_city)
        with st.container(border=True):
            # Tính tổng doanh thu và lợi nhuận theo bang
            revenue_by_city = df5.groupby("State")[["Total Sales","Operating Profit"]].sum().reset_index().sort_values(by="Total Sales", ascending=True).head(5)
            revenue_by_city['Sales %'] = (revenue_by_city['Total Sales'] / total_sales) * 100
    
            fig_col13 = go.Figure()

            fig_col13.add_trace(go.Bar(
                y=revenue_by_city['State'],
                x=revenue_by_city['Total Sales'],
                name='Doanh Thu',
                orientation='h',
                # BFF6C3
                marker=dict(color='#FFC96F'),
                text=revenue_by_city['Sales %'].apply(lambda x: f'{x:.2f}%'),
                textposition='inside',
                insidetextanchor='middle',
                hovertemplate='Doanh Thu: %{x}<br>%{text}'
            ))

            fig_col13.update_layout(
                title='Top 10 Bang Doanh Thu Cao Nhất',
                barmode='stack',
                xaxis_title='Giá Trị',
                yaxis_title='Bang',
                legend_title='Chỉ Số',
                margin=dict(t=30,r=5,l=5,b=5),
                yaxis=dict(categoryorder='total ascending'),  # Ensures the bars are ordered correctly
                bargap=0.75,
                height=300 
            )

            st.plotly_chart(fig_col13, use_container_width=True)
    col5, col6, col7 = st.columns((3))
    with col5:
        with st.container(border=True):
            #Sản phẩm doanh thu cao nhất
            # Biểu đồ doanh thu và lợi nhuận theo sản phẩm
            sales_by_product = df5.groupby('Product')[['Total Sales']].sum().reset_index().sort_values(by="Total Sales", ascending=True)
            sales_by_product['Sales %'] = (sales_by_product['Total Sales'] / total_sales) * 100
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
    with col6:
        with st.container(border=True):
            #Biểu đồ trong nhà phân phối
            sales_by_retailer = df5.groupby('Retailer')['Total Sales'].sum().reset_index()
            fig = px.pie(sales_by_retailer, values = "Total Sales", names = "Retailer", hole=0.64)
            fig.update_traces(text = sales_by_retailer["Retailer"], textposition = "inside")
            fig.update_layout(margin=dict(t=30,r=5,l=5,b=5),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                title='Nhà Bán Lẻ Có Doanh Thu Cao Nhất'
            )
            st.plotly_chart(fig,use_container_width=True)  
    with col7:
        with st.container(border=True):
            #Phương thức bán hàng có doanh thu cao nhất
            sales_by_method = df5.groupby('Sales Method')[['Total Sales']].sum().reset_index().sort_values(by="Total Sales", ascending=True)
            sales_by_method['Sales %'] = (sales_by_method['Total Sales'] / total_sales) * 100
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sales_by_method['Sales Method'],
                y=sales_by_method['Total Sales'],
                name='Doanh Thu',
                orientation='v',
                marker=dict(color='#B0DAFF'),
                text=sales_by_method['Sales %'].apply(lambda x: f'{x:.2f}%'),
                textposition='inside',
                insidetextanchor='middle',
                hovertemplate='Doanh Thu: %{x}<br>%{text}'
            ))
            # legend_title=
            fig.update_layout(
                title='Phương Thức Bán Hàng Doanh Thu Cao Nhất',
                barmode='group',
                xaxis_title='Giá Trị',
                yaxis_title='Sản Phẩm',
                margin=dict(t=30,r=5,l=5,b=5)
            )
            st.plotly_chart(fig, use_container_width=True)