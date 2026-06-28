import sys
import os
sys.path.insert(0, os.path.expanduser('~/trading-analytics'))

import pandas as pd
from sqlalchemy import create_engine
from data.loader import load_trades

DB_URL = "postgresql://neemaurassa@localhost:5432/trading_analytics"
EXCEL  = os.path.expanduser('~/trading-analytics/data/Combined closed_positions.xlsx')


def etl():
    print("Loading trades from Excel......")
    df = load_trades(EXCEL)
    print(f" {len(df) :,} clean rows loaded")

    df = df.rename(columns={
        'Order ID'    : 'order_id',
        'Instrument'  : 'instrument',
        'Type'        : 'trade_type',
        'Amount'      : 'lot_size',
        'Open Price'  : 'open_price',
        'Open Time'   : 'open_time',
        'Close Price' : 'close_price',
        'Close Time'  : 'close_time',
        'Profit'      : 'gross_profit',
        'Swap'        : 'swap',
        'Commision'   : 'commission',
        'Total Profit': 'net_profit',
        'Asset_Class' : 'asset_class',
        'Session'     : 'session',
        'Duration_mins': 'duration_mins',
        'Win'         : 'is_win',
    })
    keep = [
        'order_id', 'instrument', 'trade_type', 'lot_size',
        'open_price', 'open_time', 'close_price', 'close_time',
        'gross_profit', 'swap', 'commission', 'net_profit',
        'asset_class', 'session', 'duration_mins', 'is_win',
    ]    

    df = df[[c for c in keep if c in df.columns]]
    df['is_win'] = df['is_win'].astype(bool)

    print("Connecting to database....")
    engine = create_engine(DB_URL)

        
    df.to_sql('trades', engine, if_exists= 'replace', 
          index=False, method= 'multi', chunksize=500)

    print(f" {len(df):,} rows written to trades table")

if __name__ == "__main__":
    etl()



