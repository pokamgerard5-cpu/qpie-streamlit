import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="PnL Dashboard", layout="wide")

st.title("💰 Profit & Loss Dashboard")
st.caption("Real-time trading performance metrics")

# Initialize
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'cumulative_pnl' not in st.session_state:
    st.session_state.cumulative_pnl = 0.0
if 'outcomes' not in st.session_state:
    st.session_state.outcomes = []

# Bet size input
bet_size = st.sidebar.number_input("Bet Size ($)", min_value=10, max_value=10000, value=100, step=10)
st.sidebar.caption("This is your stake per prediction")

# Function to simulate trades based on predictions
def generate_trade_from_prediction(predicted, actual, confidence, bet_amount):
    if confidence < 0.65:
        # Skip low confidence
        return 0, "SKIPPED"
    elif predicted == actual:
        # Win
        if actual == "TIE":
            pnl = bet_amount * 2.5
        else:
            pnl = bet_amount * 0.95
        return pnl, "WIN"
    else:
        # Loss
        return -bet_amount, "LOSS"

# Main metrics display
col1, col2, col3, col4 = st.columns(4)

if st.session_state.trades:
    df_trades = pd.DataFrame(st.session_state.trades)
    
    with col1:
        st.metric("Total PnL", f"${st.session_state.cumulative_pnl:,.2f}")
    
    with col2:
        # Calculate win rate
        trades_df = df_trades[df_trades['result'] != 'SKIPPED']
        if len(trades_df) > 0:
            win_rate = (trades_df['result'] == 'WIN').sum() / len(trades_df)
            st.metric("Win Rate", f"{win_rate:.1%}")
        else:
            st.metric("Win Rate", "0%")
    
    with col3:
        st.metric("Total Trades", len(df_trades))
    
    with col4:
        avg_confidence = df_trades['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    # Equity curve
    st.subheader("📈 Equity Curve")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_trades['timestamp'],
        y=df_trades['cumulative_pnl'],
        mode='lines+markers',
        name='Portfolio Value',
        fill='tozeroy',
        line=dict(color='green', width=2)
    ))
    fig.update_layout(
        title="Cumulative PnL Over Time",
        xaxis_title="Trade Number",
        yaxis_title="Cumulative PnL ($)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent trades table
    st.subheader("📋 Recent Trades")
    st.dataframe(
        df_trades.tail(20)[['timestamp', 'predicted', 'actual', 'confidence', 'pnl', 'result']].sort_values('timestamp', ascending=False),
        use_container_width=True
    )
    
    # PnL Distribution
    st.subheader("📊 PnL Distribution")
    col_a, col_b = st.columns(2)
    
    with col_a:
        trades_only = df_trades[df_trades['result'] != 'SKIPPED']
        if len(trades_only) > 0:
            fig_hist = px.histogram(trades_only, x='pnl', nbins=20, 
                                    title="Trade PnL Distribution",
                                    color_discrete_sequence=['#2E86AB'])
            fig_hist.update_layout(xaxis_title="PnL ($)", yaxis_title="Frequency")
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with col_b:
        # Performance by outcome
        perf = df_trades[df_trades['result'] != 'SKIPPED'].groupby('predicted').agg({
            'pnl': ['count', 'mean', 'sum']
        }).round(2)
        perf.columns = ['Count', 'Avg PnL', 'Total PnL']
        st.write("Performance by Prediction Type")
        st.dataframe(perf)
    
    # Risk metrics
    st.subheader("⚠️ Risk Metrics")
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    
    # Sharpe Ratio
    returns = df_trades[df_trades['result'] != 'SKIPPED']['pnl'].values
    if len(returns) > 1:
        sharpe = (returns.mean() / returns.std()) * (252**0.5) if returns.std() > 0 else 0
        col_r1.metric("Sharpe Ratio", f"{sharpe:.2f}")
    else:
        col_r1.metric("Sharpe Ratio", "N/A")
    
    # Max Drawdown
    cumulative = df_trades['cumulative_pnl'].values
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (running_max - cumulative) / np.where(running_max > 0, running_max, 1)
    max_dd = drawdown.max()
    col_r2.metric("Max Drawdown", f"{max_dd:.1%}")
    
    # Profit Factor
    gross_profit = df_trades[df_trades['pnl'] > 0]['pnl'].sum()
    gross_loss = abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    col_r3.metric("Profit Factor", f"{profit_factor:.2f}")
    
    # Expectancy
    avg_trade = df_trades[df_trades['result'] != 'SKIPPED']['pnl'].mean()
    col_r4.metric("Avg Trade", f"${avg_trade:.2f}")
    
else:
    st.info("No trades yet. Add outcomes in 'Manual Input' and predictions will auto-track.")
    
    # Demo mode
    if st.button("🎲 Load Demo Data"):
        demo_data = []
        cum_pnl = 0
        demo_outcomes = ['P1', 'P2', 'TIE', 'P1', 'P2', 'P1', 'P1', 'P2', 'TIE', 'P1']
        demo_preds =  ['P1', 'P1', 'P1', 'P2', 'P2', 'P1', 'P1', 'P1', 'TIE', 'P1']
        demo_conf =   [0.72, 0.68, 0.45, 0.81, 0.63, 0.77, 0.82, 0.59, 0.71, 0.79]
        
        for i in range(10):
            pnl, result = generate_trade_from_prediction(demo_preds[i], demo_outcomes[i], demo_conf[i], 100)
            cum_pnl += pnl
            demo_data.append({
                'timestamp': datetime.now(),
                'predicted': demo_preds[i],
                'actual': demo_outcomes[i],
                'confidence': demo_conf[i],
                'pnl': pnl,
                'cumulative_pnl': cum_pnl,
                'result': result
            })
        
        st.session_state.trades = demo_data
        st.session_state.cumulative_pnl = cum_pnl
        st.rerun()
