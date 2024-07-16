import mysql.connector
import streamlit as st

#connection

conn=mysql.connector.connect(
    host="localhost",
    port="3307",
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
