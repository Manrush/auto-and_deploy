from datetime import datetime, timedelta
from pgdb import PGDatabase

import os
import pandas as pd
import configparser
import yfinance as yf


dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'config.ini'))

SALES_PATH = config['Files']['SALES_PATH']
COMPANIES = eval(config['Companies']['COMPANIES'])
DATABASE_CREDS = config['Database']

sales_df = pd.DataFrame()
if os.path.exists(SALES_PATH):
    sales_df = pd.read_csv(SALES_PATH)

historical_d = {}
for company in COMPANIES:
    df = yf.download(company, start=datetime.today() - timedelta(days=1), end=datetime.today()).reset_index()
    historical_d[company] = df.iloc[[-1]]
# print(historical_d)

    # os.remove(SALES_PATH)
database = PGDatabase(
    host=DATABASE_CREDS['HOST'],
    database=DATABASE_CREDS['DATABASE'],
    user=DATABASE_CREDS['USER'],
    password=DATABASE_CREDS['PASSWORD']
)

for i, row in sales_df.iterrows():
    query = f"insert into sales values('{row['dt']}', '{row['company']}', '{row['transaction_type']}',{row['amount']})"
    database.post(query)

for company, data in historical_d.items():
    for i, row in data.iterrows():
        # date_str = row['Date'].strftime('%d-%m-%Y')
        # date_str = pd.to_datetime(row['Date']).values[0].astype('datetime64[D]').astype(str)
        date_str = pd.to_datetime(row[('Date', '')]).strftime('%Y-%m-%d')
        # print(date_str)
        query = f"insert into stock values('{date_str}', '{company}', '{row['Open', company]}', {row['Close', company]})"
        database.post(query)