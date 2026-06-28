import pandas as pd
import numpy as np

Excel_path ="data/Combined closed_positions.xlsx"

JUNKS_ROWS = [
    'Name', 'Neema Urassa', 'Instrument',
    'Closed Transactions', 'Order ID'
]

NUMERICAL_COLS = [ 
    'Total Profit', 'Profit', 'Amount', 
    'Open Price', 'Close Price', 
    'Swap', 'Commision', 'S/L', 'T/P'
]


def classify_asset(instrument: str) -> str:
    if instrument in ['XAUUSD', 'XAGUSD']:
        return 'Metals'
    if instrument in ['BTCUSD.', 'ETHUSD.', 'SOLUSD.', 'LTCUSD.']:
        return 'Crypto'
    if instrument in ['NQ100.', 'WS30.', 'S&P500', 'FTSE100.']:
        return 'Indices'
    if instrument in ['WTI.']:
        return 'Commodities'
    if instrument in ['USDINDEX']:
        return 'USD Index'
    
    return 'Forex'

def classify_session(open_time: pd.Timestamp) -> str:
    h = open_time.hour
    if 0 <= h < 8:
        return 'Asian'
    elif 8 <= h < 12:
        return 'London Open'
    elif 12 <= h < 17:
        return 'New York'
    else:
        return 'London/NY Overlap'
    

def load_trades(path: str =Excel_path)-> pd.DataFrame:
    
    df= pd.read_excel(path, skiprows=3, engine='openpyxl')
    df.columns=df.columns.str.strip()


    df = df[~df['Instrument'].isin(JUNKS_ROWS)]
    df = df[df['Instrument'].notna()]


    for col in NUMERICAL_COLS:
        if col in df.columns:
            df[col]= pd.to_numeric(df[col], errors='coerce')

    df['Open Time']= pd.to_datetime(df['Open Time'], errors= 'coerce')
    df['Close Time']= pd.to_datetime(df['Close Time'], errors= 'coerce')


    df =df.dropna(subset=['Open Time', 'Close Time', 'Total Profit'])


    df = df.dropna(subset=['Open Time', 'Close Time', 'Total Profit'])

    df['Duration_mins'] = (df['Close Time'] - df['Open Time']).dt.total_seconds().div(60).round(1)
    df['Asset_Class'] = df['Instrument'].apply(classify_asset)
    df['Session'] = df ['Open Time'].apply(classify_session)
    df ['DOW'] = df['Open Time'].dt.day_name()
    df['Hour'] = df['Open Time'].dt.hour
    df['Win']= (df['Total Profit']> 0)

    df= df.sort_values('Close Time').reset_index(drop=True)
    df['Cumulative_PnL'] = df['Total Profit'].cumsum()
    peak = df['Cumulative_PnL'].cummax()
    df['Drawdown'] = df['Cumulative_PnL'] - peak

    return df




def summary_metrics(df: pd.DataFrame) -> dict:

    wins   = df[df['Total Profit'] > 0]['Total Profit']
    losses = df[df['Total Profit'] < 0]['Total Profit']

    daily_pnl = df.groupby(df['Close Time'].dt.date)['Total Profit'].sum()
    sharpe    = (daily_pnl.mean() / daily_pnl.std() * np.sqrt(252)
                 if daily_pnl.std() != 0 else 0)

    return {
        'total_trades'     : len(df),
        'net_pnl'          : round(df['Total Profit'].sum(), 2),
        'win_rate'         : round(df['Win'].mean() * 100, 1),
        'avg_win'          : round(wins.mean(), 2) if len(wins) else 0,
        'avg_loss'         : round(losses.mean(), 2) if len(losses) else 0,
        'risk_reward'      : round(abs(wins.mean() / losses.mean()), 2) if len(losses) else 0,
        'profit_factor'    : round(wins.sum() / abs(losses.sum()), 2) if losses.sum() != 0 else 0,
        'expectancy'       : round(df['Total Profit'].mean(), 2),
        'max_drawdown'     : round(df['Drawdown'].min(), 2),
        'sharpe_ratio'     : round(sharpe, 3),
        'total_commission' : round(df['Commision'].sum(), 2),
        'total_swap'       : round(df['Swap'].sum(), 2),
        'avg_duration_mins': round(df['Duration_mins'].mean(), 1),
        'date_range'       : f"{df['Open Time'].min().date()} → {df['Close Time'].max().date()}",
    }

#if __name__ == "__main__":
    df= load_trades()
    print(f"Rows       : {len(df):,}")
    print(f"Columns    : {list(df.columns)}")
    print(f"Date range : {df['Open Time'].min().date()} → {df['Close Time'].max().date()}")
    print(f"Net P&L    : ${df['Total Profit'].sum():,.2f}")
    print(f"Win rate   : {df['Win'].mean()*100:.1f}%")
    print(df.head(3))#
  
if __name__ == "__main__":
    df = load_trades()
    print(f"Rows       : {len(df):,}")
    print(f"Net P&L    : ${df['Total Profit'].sum():,.2f}")
    print(f"Win rate   : {df['Win'].mean()*100:.1f}%")

    m = summary_metrics(df)
    print("\n=== Summary Metrics ===")
    for k, v in m.items():
        print(f"  {k:<20} : {v}")
