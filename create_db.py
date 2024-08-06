import pandas as pd
from sqlalchemy import create_engine

# CSVデータの読み込み
data = pd.read_csv('data.csv')

# SQLiteデータベースへの接続
engine = create_engine('sqlite:///data.db')

# データをデータベースに保存
data.to_sql('suck', engine, if_exists='replace', index=False)
