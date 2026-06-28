import sys
import os
sys.path.insert(0, os.path.expanduser('~/trading-analytics'))


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from data.loader import load_trades, summary_metrics

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Trading Edge Analysis | Neema Urassa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colours ───────────────────────────────────────────────────
NAVY  = "#1F3864"
GOLD  = "#C9A84C"
GREEN = "#2ECC71"
RED   = "#E74C3C"
GREY  = "#7F8C8D"
LIGHT = "#F4F6F9"



# ── Custom CSS ───────────────────────────────────────────────
st.markdown(f"""
<style>
    .stApp {{ background-color: {LIGHT}; }}
    .metric-card {{
        background: white;
        border-left: 4px solid {NAVY};
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .metric-label {{
        color: {GREY};
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .metric-value {{
        color: {NAVY};
        font-size: 28px;
        font-weight: 700;
        margin-top: 4px;
    }}
    .section-header {{
        color: {NAVY};
        font-size: 20px;
        font-weight: 700;
        border-bottom: 2px solid {GOLD};
        padding-bottom: 6px;
        margin: 24px 0 16px 0;
    }}
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_trades(
        os.path.expanduser('~/trading-analytics/data/Combined closed_positions.xlsx')
    )

df  = get_data()
m   = summary_metrics(df)



# ── Sidebar filters ──────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 🔍 Filters")

    asset_classes = ["All"] + sorted(df["Asset_Class"].unique())
    sel_asset = st.selectbox("Asset Class", asset_classes)

    instruments = ["All"] + sorted(df["Instrument"].unique())
    sel_instrument = st.selectbox("Instrument", instruments)

    sessions = ["All"] + sorted(df["Session"].unique())
    sel_session = st.selectbox("Session", sessions)

    trade_types = ["All", "Buy", "Sell"]
    sel_type = st.selectbox("Trade Direction", trade_types)

    st.markdown("---")
    st.markdown("**Date Range**")
    min_date = df["Open Time"].min().date()
    max_date = df["Close Time"].max().date()
    date_range = st.date_input(
        "Select range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# ── Apply filters ─────────────────────────────────────────────
dff = df.copy()
if sel_asset != "All":
    dff = dff[dff["Asset_Class"] == sel_asset]
if sel_instrument != "All":
    dff = dff[dff["Instrument"] == sel_instrument]
if sel_session != "All":
    dff = dff[dff["Session"] == sel_session]
if sel_type != "All":
    dff = dff[dff["Type"] == sel_type]
if len(date_range) == 2:
    dff = dff[
        (dff["Open Time"].dt.date >= date_range[0]) &
        (dff["Close Time"].dt.date <= date_range[1])
    ]

dff = dff.sort_values("Close Time").reset_index(drop=True)
m   = summary_metrics(dff)



# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<h1 style='margin-bottom:4px; color:{NAVY};'>
    📊 Trading Edge Analysis
</h1>
<p style='color:{GREY}; font-size:15px; margin-top:0;'>
    Neema Urassa &nbsp;·&nbsp;
    Proprietary Trading Firm Account &nbsp;·&nbsp;
    {m['date_range']} &nbsp;·&nbsp;
    {m['total_trades']:,} trades across 36 instruments
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────
def kpi(label, value):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>"""

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(kpi("Total Trades", f"{m['total_trades']:,}"),
                     unsafe_allow_html=True)
with c2: st.markdown(kpi("Win Rate", f"{m['win_rate']}%"),
                     unsafe_allow_html=True)
with c3: st.markdown(kpi("Risk : Reward", f"{m['risk_reward']}:1"),
                     unsafe_allow_html=True)
with c4: st.markdown(kpi("Profit Factor", f"{m['profit_factor']}"),
                     unsafe_allow_html=True)
with c5: st.markdown(kpi("Avg Hold", f"{m['avg_duration_mins']} mins"),
                     unsafe_allow_html=True)
    

# ── Asset Class & Instrument ─────────────────────────────────
st.markdown('<div class="section-header">📊 Edge by Asset Class & Instrument</div>',
            unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    asset = dff.groupby('Asset_Class').agg(
        Trades=('Win', 'count'),
        Win_Rate=('Win', 'mean'),
    ).reset_index()
    asset['Win_Rate'] = (asset['Win_Rate'] * 100).round(1)
    asset['Edge_Score'] = (asset['Win_Rate'] * asset['Trades'] / 100).round(1)
    asset = asset.sort_values('Win_Rate', ascending=True)

    colors = ['#2ECC71' if w >= 50 else '#E74C3C' for w in asset['Win_Rate']]

    fig = go.Figure(go.Bar(
        y=asset['Asset_Class'],
        x=asset['Win_Rate'],
        orientation='h',
        marker_color=colors,
        text=asset['Win_Rate'].apply(lambda x: f"{x}%"),
        textposition='outside',
    ))
    fig.add_vline(x=50, line_dash='dash', line_color=GREY)
    fig.update_layout(
        title='Win Rate by Asset Class',
        height=320,
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis_title='Win Rate (%)', yaxis_title='',
        xaxis_range=[0, 80],
        margin=dict(l=5, r=60, t=40, b=5)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    inst = dff.groupby('Instrument').agg(
        Trades=('Win', 'count'),
        Win_Rate=('Win', 'mean'),
    ).reset_index()
    inst['Win_Rate'] = (inst['Win_Rate'] * 100).round(1)
    inst = inst[inst['Trades'] >= 10].sort_values('Win_Rate', ascending=True)

    colors_i = ['#2ECC71' if w >= 55 else '#C9A84C' if w >= 50 else '#E74C3C'
                for w in inst['Win_Rate']]

    fig2 = go.Figure(go.Bar(
        y=inst['Instrument'],
        x=inst['Win_Rate'],
        orientation='h',
        marker_color=colors_i,
        text=inst['Win_Rate'].apply(lambda x: f"{x}%"),
        textposition='outside',
    ))
    fig2.add_vline(x=50, line_dash='dash', line_color=GREY)
    fig2.update_layout(
        title='Win Rate by Instrument (min 10 trades)',
        height=320,
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis_title='Win Rate (%)', yaxis_title='',
        xaxis_range=[0, 85],
        margin=dict(l=5, r=60, t=40, b=5)
    )
    st.plotly_chart(fig2, use_container_width=True)


    # ── Session & Day of Week ─────────────────────────────────────
st.markdown('<div class="section-header">⏰ When Does Edge Appear?</div>',
            unsafe_allow_html=True)

col_c, col_d = st.columns(2)

with col_c:
    session = dff.groupby('Session').agg(
        Trades=('Win', 'count'),
        Win_Rate=('Win', 'mean'),
    ).reset_index()
    session['Win_Rate'] = (session['Win_Rate'] * 100).round(1)
    colors_s = ['#2ECC71' if w >= 50 else '#E74C3C' for w in session['Win_Rate']]

    fig3 = go.Figure(go.Bar(
        x=session['Session'],
        y=session['Win_Rate'],
        marker_color=colors_s,
        text=session['Win_Rate'].apply(lambda x: f"{x}%"),
        textposition='outside',
    ))
    fig3.add_hline(y=50, line_dash='dash', line_color=GREY)
    fig3.update_layout(
        title='Win Rate by Session',
        height=320,
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis_title='Win Rate (%)', xaxis_title='',
        yaxis_range=[0, 70],
        margin=dict(l=5, r=5, t=40, b=5)
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    dow = dff[dff['DOW'].isin(dow_order)].groupby('DOW').agg(
        Trades=('Win', 'count'),
        Win_Rate=('Win', 'mean'),
    ).reindex(dow_order).reset_index()
    dow['Win_Rate'] = (dow['Win_Rate'] * 100).round(1)
    colors_d = ['#2ECC71' if w >= 50 else '#E74C3C' for w in dow['Win_Rate']]

    fig4 = go.Figure(go.Bar(
        x=dow['DOW'],
        y=dow['Win_Rate'],
        marker_color=colors_d,
        text=dow['Win_Rate'].apply(lambda x: f"{x}%"),
        textposition='outside',
    ))
    fig4.add_hline(y=50, line_dash='dash', line_color=GREY)
    fig4.update_layout(
        title='Win Rate by Day of Week',
        height=320,
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis_title='Win Rate (%)', xaxis_title='',
        yaxis_range=[0, 70],
        margin=dict(l=5, r=5, t=40, b=5)
    )
    st.plotly_chart(fig4, use_container_width=True)


    # ── Hold Duration & Concentrated Portfolio ───────────────────
st.markdown('<div class="section-header">🎯 Hold Duration & Edge Concentration</div>',
            unsafe_allow_html=True)

col_e, col_f = st.columns(2)

with col_e:
    dff['Duration_Bucket'] = pd.cut(
        dff['Duration_mins'],
        bins=[0, 15, 60, 240, 1440, 99999],
        labels=['< 15 min', '15–60 min', '1–4 hrs', '4–24 hrs', '> 1 Day']
    )
    duration = dff.groupby('Duration_Bucket', observed=True).agg(
        Trades=('Win', 'count'),
        Win_Rate=('Win', 'mean'),
    ).reset_index()
    duration['Win_Rate'] = (duration['Win_Rate'] * 100).round(1)
    colors_dur = ['#2ECC71' if w >= 50 else '#E74C3C' for w in duration['Win_Rate']]

    fig5 = go.Figure(go.Bar(
        x=duration['Duration_Bucket'].astype(str),
        y=duration['Win_Rate'],
        marker_color=colors_dur,
        text=duration['Win_Rate'].apply(lambda x: f"{x}%"),
        textposition='outside',
    ))
    fig5.add_hline(y=50, line_dash='dash', line_color=GREY)
    fig5.update_layout(
        title='Win Rate by Hold Duration',
        height=320,
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis_title='Win Rate (%)', xaxis_title='',
        yaxis_range=[0, 75],
        margin=dict(l=5, r=5, t=40, b=5)
    )
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    # Concentrated portfolio simulation
    inst_wr = dff.groupby('Instrument').agg(
        Trades=('Win', 'count'),
        Win_Rate=('Win', 'mean'),
    ).reset_index()
    inst_wr['Win_Rate'] = (inst_wr['Win_Rate'] * 100).round(1)
    high_edge = inst_wr[
        (inst_wr['Win_Rate'] >= 55) &
        (inst_wr['Trades'] >= 10)
    ]['Instrument'].tolist()

    dff_concentrated = dff[dff['Instrument'].isin(high_edge)]

    full_wr   = round(dff['Win'].mean() * 100, 1)
    conc_wr   = round(dff_concentrated['Win'].mean() * 100, 1) \
                if len(dff_concentrated) > 0 else 0

    fig6 = go.Figure(go.Bar(
        x=['Full Portfolio\n(all instruments)',
           f'Concentrated\n({len(high_edge)} instruments)'],
        y=[full_wr, conc_wr],
        marker_color=[RED, GREEN],
        text=[f"{full_wr}%", f"{conc_wr}%"],
        textposition='outside',
    ))
    fig6.add_hline(y=50, line_dash='dash', line_color=GREY)
    fig6.update_layout(
        title='Full vs Concentrated Portfolio Win Rate',
        height=320,
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis_title='Win Rate (%)', xaxis_title='',
        yaxis_range=[0, 80],
        margin=dict(l=5, r=5, t=40, b=5)
    )
    st.plotly_chart(fig6, use_container_width=True)


    # ── Trade Log ────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Trade Log</div>',
            unsafe_allow_html=True)

display_cols = [
    'Order ID', 'Instrument', 'Type', 'Amount',
    'Open Time', 'Close Time', 'Duration_mins',
    'Asset_Class', 'Session', 'Win'
]
display_cols = [c for c in display_cols if c in dff.columns]

st.dataframe(
    dff[display_cols]
      .rename(columns={'Duration_mins': 'Duration (min)'})
      .sort_values('Close Time', ascending=False)
      .reset_index(drop=True),
    use_container_width=True,
    height=320,
)

# ── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<p style='text-align:center; color:{GREY}; font-size:13px;'>
    Built by <strong>Neema Urassa</strong> · Finance Data Analyst ·
    <a href='https://github.com/newissa1' target='_blank'>GitHub</a> ·
    <a href='https://www.linkedin.com/in/neema-urassa' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
