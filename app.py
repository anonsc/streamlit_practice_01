from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import numpy as np
import bcrypt
import plotly.graph_objects as go
import logging
import traceback

logging.basicConfig(filename='error.log', level=logging.ERROR)

HASHED_PASSWORD = b'$2b$12$2UpvaTXQ4hzpXeXabX5WgeXhrFU/oem87UbUIP2CFgnien006Mzzq'

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def safe_execution(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error: {e}\n{traceback.format_exc()}")
            st.error("An error occurred. Please try again later.")
    return wrapper

def log_in():
    st.header("Please enter the password to access this application")

    # フォームを作成
    with st.form("login_form"):
        password = st.text_input("Password", type="password", max_chars=20)  # 文字数制限を追加
        submit_button = st.form_submit_button("Submit")

    # フォームが送信されたときの処理
    @safe_execution
    def authenticate():
        if submit_button:
            # パスワードの検証
            if bcrypt.checkpw(password.encode(), HASHED_PASSWORD):
                st.session_state.authenticated = True
                st.rerun()  # ページを再実行してUIを更新
            else:
                st.error("Incorrect password. Please try again.")

    authenticate()


def show_contents():

    engine = create_engine('sqlite:///data.db')

    query = "SELECT * FROM suck"
    data = pd.read_sql(query, engine)

    @st.cache_data
    def load_data():
        query = "SELECT * FROM suck"
        data = pd.read_sql(query, engine)
        data['datetime'] = pd.to_datetime(data['datetime'])
        return data

    data = load_data()

    # サイドバーの設定
    st.sidebar.header("Filter Options")
    start_date = st.sidebar.date_input("Start datetime", value=data["datetime"].min())
    end_date = st.sidebar.date_input("End datetime", value=data["datetime"].max())
    lower_temp = st.sidebar.number_input('Lower temperature', value=data['avg_temp'].min())
    upper_temp = st.sidebar.number_input('Upper temperature', value=data['avg_temp'].max())

    # データのフィルタリング
    filtered_data = data[
        (data["avg_temp"] <= upper_temp) &
        (data["avg_temp"] >= lower_temp) &
        (data["datetime"] >= pd.to_datetime(start_date)) &
        (data["datetime"] <= pd.to_datetime(end_date))
    ]

    # フィルタリングされたデータの表示
    st.header("Filtered Data")
    st.write(filtered_data)

    average_temp = filtered_data['avg_temp'].mean()
    st.header("Average Temperature")
    st.metric(label='Average Temperaturee', value=f"{average_temp:.2f} °C")

    # グラフの作成
    st.header("Temperature Over Time")
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_data['datetime'],
        y=filtered_data['avg_temp'],
        mode='lines+markers',
        name='Avg Temp'
    ))

    fig.update_layout(
        title="Temperature Over Time",
        xaxis_title="Datetime",
        yaxis_title="Average Temperature",
        xaxis=dict(
            tickformat='%Y-%m-%d',
            tickangle=45
        ),
        showlegend=True
    )

    st.plotly_chart(fig)
print(st.session_state)

if not st.session_state.authenticated:
    log_in()

else:
    show_contents()

    @safe_execution
    def logout():
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()  # ログアウト後にページを再実行してUIを更新

    logout()
