import mysql.connector
import streamlit as st

#connection

conn=mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    passwd="",
    db="datn_dss"
)
c=conn.cursor()

#fetch

def view_all_data():
    c.execute('select * from adidas_4 order by id asc')
    data=c.fetchall()
    return data

def update_data_to_mysql(df):
    # Chèn dữ liệu vào bảng
    for i, row in df.iterrows():
        sql = """
            INSERT INTO adidas_ (Retailer, Region, State, City, Product, `Price per Unit`, `Units Sold`, `Operating Profit`, `Sales Method`, `Total Sales`, Month, Year, Day, Season, Date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        c.execute(sql, tuple(row))

    conn.commit()
    cursor.close()
    conn.close()
    st.write("Dữ liệu đã được cập nhật lên MySQL")