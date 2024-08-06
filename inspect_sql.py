import streamlit as st
from sqlalchemy import create_engine, inspect

# SQLiteデータベースへの接続
engine = create_engine('sqlite:///data.db')

# データベースのインスペクターを作成
inspector = inspect(engine)

# テーブルの一覧を取得
tables = inspector.get_table_names()

# Streamlitアプリケーション
st.header("データベースのテーブル一覧")
st.write("データベースに存在するテーブル:")
for table in tables:
    st.write(table)
