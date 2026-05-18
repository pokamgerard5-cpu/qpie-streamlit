import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="PnL", layout="wide")

st.title("💰 Profit & Loss")

# Initialize
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'cum_pnl' not in st.session_state:
    st.session_state.cum_pnl = 0.0

bet = st.sidebar.number_input("Bet Size ($)", 10, 1000, 100)

if st.session_state.trades:
    df = pd.DataFrame(st.session_state.trades)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total PnL", f"${st.session_state.cum_pnl:,.2f}")
    
    trades_df = df[df['result'] != 'SKIP']
    if len(trades_df) > 0:
        win_rate = (trades_df['result'] == 'WIN').sum() / len(trades_df)
        col2.metric("Win Rate", f"{win_rate:.1%}")
    
    col3.metric("Total Trades", len(df))
    
    # Recent trades
    st.subheader("Recent Trades")
    st.dataframe(df.tail(10)[['time', 'pred', 'actual', 'pnl', 'result']])
    
else:
    st.info("No trades yet. Record rounds in Input page.")
    
    if st.button("Add Demo Data"):
        demo = []
        cum = 0
        for i in range(5):
            pnl = np.random.choice([-100, 95, 95])
            cum += pnl
            demo.append({
                'time': datetime.now(),
                'pred': 'P1',
                'actual': np.random.choice(['P1', 'P2', 'TIE']),
                'pnl': pnl,
                'cumulative': cum,
                'result': 'WIN' if pnl > 0 else 'LOSS'
            })
        st.session_state.trades = demo
        st.session_state.cum_pnl = cum
        st.rerun()
