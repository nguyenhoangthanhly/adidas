import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import sys
import folium
from streamlit_folium import st_folium
from streamlit_extras.metric_cards import style_metric_cards
import src.query as query

def OverView(original_path):
    # st.write("OverView")
    def format_sales(value):
        """Format the sales value with appropriate unit (M for million, B for billion)."""
        if value >= 1e9:
            return f"{value / 1e9:.2f}B"
        elif value >= 1e6:
            return f"{value / 1e6:.2f}M"
        else:
            return f"{value:,.0f}"
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

    col1, col2, col3, col4, col5 = st.columns((5))
    df["Date"] = pd.to_datetime(df["Date"])

    # Getting the min and max date 
    startDate = pd.to_datetime(df["Date"]).min()
    endDate = pd.to_datetime(df["Date"]).max()

    with col5:
        with st.container(border=True):
            date1 = pd.to_datetime(st.date_input("Start Date", startDate))

        with st.container(border=True):
            date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()
    
    total_sales = float(pd.Series(df['Total Sales']).sum())
    total_opearatingProfit = float(pd.Series(df['Operating Profit']).sum())
    total_product = float(pd.Series(df['Units Sold']).sum())
    total_transactions = float(df.shape[0])
    with col1:
        # Toongr doanh thu
        with st.container(border=True):
            format_sales = format_sales(total_sales)
            st.info('Total Sales',icon="💰")
            st.metric(label="",value=format_sales)

    with col2:
        # Tổng lợi nhuận
        with st.container(border=True):
            st.info('Total Operating Profit',icon="💰")
            st.metric(label="",value=f"{total_opearatingProfit:,.0f}")

    with col3:
        # Tổng số sản phẩm bán ra
        with st.container(border=True):
            st.info('Total Amount Product',icon="💰")
            st.metric(label="",value=f"{total_product:,.0f}")

    with col4:
        # Tổng số giao dịch
        with st.container(border=True):
            st.info('Total Transactions', icon="💰")
            st.metric(label="", value=f"{total_transactions:,.0f}")
    style_metric_cards(background_color="#FFFFFF",border_left_color="#1E90FF",border_color="#FFFFFF",box_shadow="#1E90FF")

    col6, col7 = st.columns([4,6])
    with col6:
        col_sales_year_growth, col_profit_year_growth = st.columns(2)
        with col_sales_year_growth:
            with st.container(border=True, height=200):
                sales_by_year = df.groupby('Year')['Total Sales'].sum().reset_index()
                if len(sales_by_year) >= 2:
                    current_year_sales = sales_by_year.iloc[-1]['Total Sales']
                    previous_year_sales = sales_by_year.iloc[-2]['Total Sales']
                    growth_percentage = ((current_year_sales - previous_year_sales) / previous_year_sales) * 100
                else:
                    current_year_sales = 0
                    previous_year_sales = 0
                    growth_percentage = 0
                # Biểu đồ chỉ báo phần trăm tăng trưởng
                fig_gauge = go.Figure()
                fig_gauge.add_trace(go.Indicator(
                    mode="gauge+number+delta",
                    value=current_year_sales,
                    delta={'reference': previous_year_sales, 'relative': True},
                    gauge={
                        'axis': {'visible': False}},
                    domain={'x': [0.1, 0.9], 'y': [0.5, 0.9]}
                ))
                fig_gauge.update_layout(
                    margin=dict(t=30,r=5,l=5,b=5), 
                    title='TDTT-DT Năm Hiên Tại / Trước',
                    height=300,
                    width=300,
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
        with col_profit_year_growth:
            with st.container(border=True, height=200):
                sales_by_year = df.groupby('Year')['Operating Profit'].sum().reset_index()
                if len(sales_by_year) >= 2:
                    current_year_sales = sales_by_year.iloc[-1]['Operating Profit']
                    previous_year_sales = sales_by_year.iloc[-2]['Operating Profit']
                    growth_percentage = ((current_year_sales - previous_year_sales) / previous_year_sales) * 100
                else:
                    current_year_sales = 0
                    previous_year_sales = 0
                    growth_percentage = 0
                # Biểu đồ chỉ báo phần trăm tăng trưởng
                fig_gauge = go.Figure()
                fig_gauge.add_trace(go.Indicator(
                    mode="gauge+number+delta",
                    value=current_year_sales,
                    delta={'reference': previous_year_sales, 'relative': True},
                    gauge={
                        'axis': {'visible': False}},
                    domain={'x': [0.1, 0.9], 'y': [0.5, 0.9]}
                ))
                fig_gauge.update_layout(
                    margin=dict(t=30,r=5,l=5,b=5), 
                    title='TDTT-LN Năm Hiên Tại / Trước',
                    height=300,
                    width=300,
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
        with st.container(border=True):
             # Biểu đồ doanh thu và lợi nhuận theo sản phẩm
            sales_profit_by_product = df.groupby('Product')[['Total Sales', 'Operating Profit']].sum().reset_index()
            sales_profit_by_product['Sales %'] = (sales_profit_by_product['Total Sales'] / total_sales) * 100
            sales_profit_by_product['Operating Profit'] = sales_profit_by_product['Operating Profit'].astype(float)
            sales_profit_by_product['Profit %'] = (sales_profit_by_product['Operating Profit'] / total_opearatingProfit) * 100
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=sales_profit_by_product['Product'],
                x=sales_profit_by_product['Total Sales'],
                name='Doanh Thu',
                orientation='h',
                marker=dict(color='#1E90FF'),
                text=sales_profit_by_product['Sales %'].apply(lambda x: f'{x:.2f}%'),
                textposition='inside',
                insidetextanchor='middle',
                hovertemplate='Doanh Thu: %{x}<br>%{text}'
            ))
            fig.add_trace(go.Bar(
                y=sales_profit_by_product['Product'],
                x=sales_profit_by_product['Operating Profit'],
                name='Lợi Nhuận',
                orientation='h',
                marker=dict(color='#FFC7ED'),
                text=sales_profit_by_product['Profit %'].apply(lambda x: f'{x:.2f}%'),
                textposition='auto',
                insidetextanchor='middle',
                hovertemplate='Lợi Nhuận: %{x}<br>%{text}'
            ))
            
            fig.update_layout(
                title='Doanh Thu-Lợi Nhuận Theo Sản Phẩm',
                barmode='group',
                xaxis_title='Giá Trị',
                yaxis_title='Sản Phẩm',
                margin=dict(t=30,r=5,l=5,b=5),
                height=520,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.2
                ),
            )
            st.plotly_chart(fig, use_container_width=True)
    with col7:
        with st.container(border=True):
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
            fig_time.add_trace(go.Scatter(
                x=sales_profit_quarter_data['Label'],
                y=sales_profit_quarter_data['Operating Profit'],
                mode='lines',
                name='Lợi Nhuận',
                line=dict(color='red')
            ))

            fig_time.update_layout(
                title='Doanh Thu và Lợi Nhuận Theo Thời Gian',
                xaxis_title='Thời Gian',
                yaxis_title='Giá Trị',
                margin=dict(t=30,r=5,l=5,b=5),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                height=500
            )

            st.plotly_chart(fig_time, use_container_width=True)
        col_agv_sales_by_year, col_agv_profit_by_year = st.columns(2)
        with col_agv_sales_by_year:
            with st.container(border=True):
                agg_sale_by_month = df.groupby(['Month'])['Total Sales'].sum().mean()
                st.info('Average Sales By Month',icon="💰")
                st.metric(label="",value=f"{agg_sale_by_month:,.0f}")
        with col_agv_profit_by_year:
            with st.container(border=True):
                agg_profit_by_month = df.groupby(['Month'])['Operating Profit'].sum().mean()
                st.info('Average Profit By Month',icon="💰")
                st.metric(label="",value=f"{agg_profit_by_month:,.0f}")

    col8, col9 = st.columns([3.5,7])
    col10, col11 = st.columns([5,4])
    col14, col15 = st.columns(2)
    col12, col13 = st.columns(2)
    with col8:
        with st.container(border=True):
            sales_by_method = df.groupby('Sales Method')['Total Sales'].sum().reset_index()
            profit_by_method = df.groupby('Sales Method')['Operating Profit'].sum().reset_index()

            fig = go.Figure()
            colors_profit = {'In-store': '#87CEFA', 'Online': '#00BFFF', 'Outlet': '#1E90FF'}
            fig.add_trace(go.Pie(
                labels=sales_by_method['Sales Method'],
                values=sales_by_method['Total Sales'],
                name="Doanh Thu",
                hole=0.8,
                domain={'x': [0, 1], 'y': [0, 1]},
                textinfo='percent',
                textposition='inside',
                insidetextorientation='radial',
                marker=dict(colors=list(colors_profit.values())
                            ),
                hoverinfo='label+percent+name',
                hovertemplate='Doanh Thu: %{label}<br>Percentage: %{percent}<br>Value: %{value}<extra></extra>'            
            ))

            # Biểu đồ tròn cho lợi nhuận (được thu nhỏ để nằm bên trong biểu đồ doanh thu)
            fig.add_trace(go.Pie(
                labels=profit_by_method['Sales Method'],
                values=profit_by_method['Operating Profit'],
                name="Lợi Nhuận",
                hole=0.5,
                domain={'x': [0.15, 0.85], 'y': [0.15, 0.85]},
                textinfo='percent',
                textposition='inside',
                insidetextorientation='radial',
                marker=dict(colors=list(colors_profit.values())
                            ),
                hoverinfo='label+percent+name',
                hovertemplate='Lợi Nhuận: %{label}<br>Percentage: %{percent}<br>Value: %{value}<extra></extra>'
            ))

            fig.add_annotation(
                text="Doanh Thu",
                xref="paper", yref="paper",
                x=0.5, y=1.1,  # Vị trí của chú thích (ở giữa và dưới biểu đồ)
                showarrow=False,
                font=dict(size=14)
            )

            # Thêm chú thích cho lợi nhuận
            fig.add_annotation(
                text="Lợi Nhuận",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            # Cập nhật bố cục cho biểu đồ
            fig.update_layout(
                title="Doanh Thu - Lợi Nhuận Theo Phương Pháp Bán Hàng",
                showlegend=True,
                margin=dict(t=80,r=5,l=5,b=5,),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

    with col9:
        with st.container(border=True):
            quarter_data = df.groupby(['Year', 'Season']).agg({
                'Total Sales': 'sum',
                'Operating Profit': 'sum'
            }).reset_index()

            # Tạo nhãn cho trục x
            quarter_data['Label'] = quarter_data.apply(lambda row: f"Năm {row['Year']} - Quý {row['Season']}", axis=1)

            # Tính tốc độ tăng trưởng doanh thu theo từng quý trong năm
            quarter_data['Growth Rate'] = quarter_data['Total Sales'].pct_change() * 100
            # quarter_data['Profit Growth Rate'] = quarter_data['Operating Profit'].pct_change() * 100

            fig_time2 = go.Figure()
            fig_time2.add_trace(go.Bar(
                    y=quarter_data['Total Sales'],
                    yaxis='y',
                    x=quarter_data['Label'],
                    name='Doanh Thu',
                    orientation='v',
                    marker=dict(color='#1E90FF'),
                    text=quarter_data['Total Sales'],
                    textposition='inside',
                    insidetextanchor='middle',
                    #hovertemplate='Doanh Thu: %{x}<br>%{text}'
                ))
            fig_time2.add_trace(go.Bar(
                    y=quarter_data['Operating Profit'],
                    yaxis='y',
                    x=quarter_data['Label'],
                    name='Lợi Nhuận',
                    orientation='v',
                    marker=dict(color='#FFC96F'),
                    text=quarter_data['Operating Profit'],
                    textposition='inside',
                    insidetextanchor='middle',
                    #hovertemplate='Lợi Nhuận: %{x}<br>%{text}'
            ))
            fig_time2.add_trace(go.Scatter(
                x=quarter_data['Label'],
                y=quarter_data['Growth Rate'],
                yaxis='y2',
                mode='lines+markers',
                name='TĐTT Doanh thu',
                line=dict(color='#FF0000'),
                text=quarter_data['Growth Rate'],
                #textposition='center'
            ))
            fig_time2.update_layout(
                title='Doanh Thu, Lợi Nhuận và Tốc Độ Tăng Trưởng Theo Từng Quý',
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
                    showgrid=False
                ),
                # legend_title=dict(),
                barmode='group',
                margin=dict(t=30,r=5,l=5,b=5),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5,
                ),
            )

            st.plotly_chart(fig_time2, use_container_width=True) 
    
    with col10:
        with st.container(border=True, height=330):
            # Bản đồ thế giới thể hiện doanh thu theo từng bang
            state_sales = df.groupby("State")["Total Sales"].sum().reset_index()
            m = folium.Map(location=[38, -95], zoom_start=3.4, scrollWheelZoom=True)
            us_state_json = os.path.join(original_path, 'data', 'us_state.json')
            choropleth = folium.Choropleth(
                geo_data = us_state_json,
                name="choropleth",
                data=state_sales,
                columns=["State", "Total Sales"],
                key_on="feature.properties.name",
                # fill_color="YlGn",
                fill_opacity=0.8,
                line_opacity=0.2,
                legend_name="Unemployment Rate (%)",
            )
            choropleth.geojson.add_to(m)
            choropleth.geojson.add_child(
                folium.features.GeoJsonTooltip(['name'], labels=False)
            )
            # Thêm các tooltip tùy chỉnh
            for feature in choropleth.geojson.data['features']:
                state_name = feature['properties']['name']
                sales = state_sales[state_sales['State'] == state_name]['Total Sales'].values
                if len(sales) > 0:
                    feature['properties']['tooltip'] = f'{state_name}: ${sales[0]:,.2f}'

            choropleth.geojson.add_child(
                folium.features.GeoJsonTooltip(
                    fields=['tooltip'],
                    labels=False
                )
            )
            st_folium(m, height=300, width=700)
        with st.container(border=True):
            option = st.radio("Chọn hiển thị", ('State cao nhất', 'State thấp nhất'), horizontal=True)
            revenue_by_state = df.groupby("State")[["Total Sales","Operating Profit"]].sum().reset_index()
            revenue_by_state['Sales %'] = (revenue_by_state['Total Sales'] / total_sales) * 100
            revenue_by_state['Profit %'] = (revenue_by_state['Operating Profit'] / total_opearatingProfit) * 100
            if option == "State cao nhất":
                top5_state_max = revenue_by_state.sort_values(by='Total Sales', ascending=False).head(5)
                st.markdown("""
                    <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Top 5 Bang Doanh Thu - Lợi Nhuận Cao Nhất</h6>
                    """, unsafe_allow_html=True)
                st.dataframe(
                    top5_state_max, width=700
                )
            if option == "State thấp nhất":
                top5_state_min = revenue_by_state.sort_values(by='Total Sales', ascending=False).tail(5)
                st.markdown("""
                    <h6 style="text-align: center; font-size: 15px; font-weight: bold;">Top 5 Bang Doanh Thu - Lợi Nhuận Thấp Nhất</h6>
                    """, unsafe_allow_html=True)
                st.dataframe(
                    top5_state_min, width=700
                )
    with col11:
        with st.container(border=True):
            # Tính toán phần trăm doanh thu và lợi nhuận theo từng vùng
            sales_profit_by_region = df.groupby('Region')[['Total Sales', 'Operating Profit']].sum().reset_index()
            sales_profit_by_region['Sales %'] = (sales_profit_by_region['Total Sales'] / total_sales) * 100
            sales_profit_by_region['Profit %'] = (sales_profit_by_region['Operating Profit'] / total_opearatingProfit) * 100

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sales_profit_by_region['Region'],
                y=sales_profit_by_region['Total Sales'],
                mode='lines+markers',
                name='Doanh Thu',
                # fill='tozeroy'
            ))
            fig.add_trace(go.Scatter(
                x=sales_profit_by_region['Region'],
                y=sales_profit_by_region['Operating Profit'],
                mode='lines+markers',
                name='Lợi Nhuận',
                # fill='tozeroy'
            ))
            fig.update_layout(
                title='Doanh Thu-Lợi Nhuận Theo Vùng',
                barmode='stack',
                xaxis_title='Vùng',
                yaxis_title='Giá trị',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(t=30,r=5,l=5,b=5),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True) 
        with st.container(border=True):
            # Tạo radio button để chọn hiển thị doanh thu cao nhất hoặc thấp nhất
            option = st.radio("Chọn hiển thị", ('City cao nhất', 'City thấp nhất'), horizontal=True)
            # Tính tổng doanh thu và lợi nhuận theo bang
            revenue_by_city = df.groupby("City")[["Total Sales","Operating Profit"]].sum().reset_index()
            revenue_by_city['Sales %'] = (revenue_by_city['Total Sales'] / total_sales) * 100
            revenue_by_city['Profit %'] = (revenue_by_city['Operating Profit'] / total_opearatingProfit) * 100
            fig_col13 = go.Figure()
            if option == "City cao nhất":
                top5_city_max = revenue_by_city.sort_values(by='Total Sales', ascending=False).head(5)
                fig_col13.add_trace(go.Bar(
                    x=top5_city_max['City'],
                    y=top5_city_max['Total Sales'],
                    name='Doanh Thu',
                    orientation='v',
                    marker=dict(color='#1E90FF'),
                    text=top5_city_max['Sales %'].apply(lambda x: f'{x:.2f}%'),
                    textposition='inside',
                    insidetextanchor='middle',
                    # hovertemplate='Doanh Thu: %{x}<br>%{text}'
                    hovertemplate='<b>%{x}</b><br>Doanh Thu: %{y}<br>Percentage: %{text}<extra></extra>'
                ))

                fig_col13.add_trace(go.Bar(
                    x=top5_city_max['City'],
                    y=top5_city_max['Operating Profit'],
                    name='Lợi Nhuận',
                    orientation='v',
                    marker=dict(color='#FFC96F'),
                    text=top5_city_max['Profit %'].apply(lambda x: f'{x:.2f}%'),
                    textposition='inside',
                    insidetextanchor='middle',
                    # hovertemplate='Lợi Nhuận: %{x}<br>%{text}'
                    hovertemplate='<b>%{x}</b><br>Lợi Nhuận: %{y}<br>Percentage: %{text}<extra></extra>'
                ))

                fig_col13.update_layout(
                    title='Top 5 Thành Phố Doanh Thu-Lợi Nhuận Cao Nhất',
                    # barmode='stack',
                    barmode = "group",
                    yaxis_title='Giá Trị',
                    xaxis_title='Thành Phố',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(t=30,r=5,l=5,b=5),
                    height = 350
                )

                st.plotly_chart(fig_col13, use_container_width=True)
            if option == "City thấp nhất":
                top5_city_max = revenue_by_city.sort_values(by='Total Sales', ascending=False).tail(5)
                fig_col13.add_trace(go.Bar(
                    x=top5_city_max['City'],
                    y=top5_city_max['Total Sales'],
                    name='Doanh Thu',
                    orientation='v',
                    marker=dict(color='#1E90FF'),
                    text=top5_city_max['Sales %'].apply(lambda x: f'{x:.2f}%'),
                    textposition='inside',
                    insidetextanchor='middle',
                    # hovertemplate='Doanh Thu: %{x}<br>%{text}'
                    hovertemplate='<b>%{x}</b><br>Doanh Thu: %{y}<br>Percentage: %{text}<extra></extra>'
                ))

                fig_col13.add_trace(go.Bar(
                    x=top5_city_max['City'],
                    y=top5_city_max['Operating Profit'],
                    name='Lợi Nhuận',
                    orientation='v',
                    marker=dict(color='#FFC96F'),
                    text=top5_city_max['Profit %'].apply(lambda x: f'{x:.2f}%'),
                    textposition='inside',
                    insidetextanchor='middle',
                    # hovertemplate='Lợi Nhuận: %{x}<br>%{text}'
                    hovertemplate='<b>%{x}</b><br>Lợi Nhuận: %{y}<br>Percentage: %{text}<extra></extra>'
                ))

                fig_col13.update_layout(
                    title='Top 5 Thành Phố Doanh Thu-Lợi Nhuận Cao Nhất',
                    # barmode='stack',
                    barmode = "group",
                    yaxis_title='Giá Trị',
                    xaxis_title='Thành Phố',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(t=30,r=5,l=5,b=5),
                    height = 350
                )

                st.plotly_chart(fig_col13, use_container_width=True)

                

                