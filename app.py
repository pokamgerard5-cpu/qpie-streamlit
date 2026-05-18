import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import os

# Page config
st.set_page_config(
    page_title="QPIE - Probability Intelligence Engine",
    page_icon="🎲",
    layout="wide"
)

# Initialize session state
if 'outcomes' not in st.session_state:
    # Try to load from persistent storage
    persistent_path = os.path.join(os.path.expanduser("~"), ".streamlit", "outcomes.csv")
    if os.path.exists(persistent_path):
        df = pd.read_csv(persistent_path)
        st.session_state.outcomes = df.to_dict('records')
    else:
        st.session_state.outcomes = []

if 'pnl' not in st.session_state:
    st.session_state.pnl = 0.0
    
if 'trades' not in st.session_state:
    st.session_state.trades = []

# Title
st.title("🎲 QPIE - Quantum Probability Intelligence Engine")
st.caption("Hedge-Fund Grade RNG Analytics | Real-Time Probability Intelligence")

# Sidebar
with st.sidebar:
    st.header("📊 System Status")
    st.metric("Total Rounds Logged", len(st.session_state.outcomes))
    st.metric("Cumulative PnL", f"${st.session_state.pnl:.2f}")
    
    st.divider()
    st.subheader("⚙️ Settings")
    confidence_threshold = st.slider("Min Confidence to Bet", 0.5, 0.95, 0.65, key="conf_thresh")
    risk_per_trade = st.slider("Risk per Trade ($)", 10, 500, 100, key="risk_amount")
    
    if st.button("💾 Export Data"):
        if st.session_state.outcomes:
            df = pd.DataFrame(st.session_state.outcomes)
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "qpie_data.csv", key="download_btn")

# Main metrics
st.subheader("🎯 Current Predictions")

if len(st.session_state.outcomes) >= 5:
    # Simple probability calculation
    df = pd.DataFrame(st.session_state.outcomes[-50:])  # Last 50 rounds
    recent = df.tail(20)
    
    p1_count = recent[recent['outcome'] == 'P1'].shape[0]
    p2_count = recent[recent['outcome'] == 'P2'].shape[0]
    tie_count = recent[recent['outcome'] == 'TIE'].shape[0]
    total = len(recent)
    
    prob_p1 = p1_count / total if total > 0 else 0.33
    prob_p2 = p2_count / total if total > 0 else 0.33
    prob_tie = tie_count / total if total > 0 else 0.34
    
    # Calculate confidence based on historical accuracy
    confidence = max(prob_p1, prob_p2, prob_tie) * 0.85
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🏆 Player 1", f"{prob_p1:.1%}")
    col2.metric("🏆 Player 2", f"{prob_p2:.1%}")
    col3.metric("⚖️ Tie", f"{prob_tie:.1%}")
    
    st.progress(confidence)
    st.caption(f"Prediction Confidence: {confidence:.1%}")
    
    if confidence < confidence_threshold:
        st.warning(f"⚠️ Low confidence ({confidence:.1%} < {confidence_threshold:.0%}) - Consider skipping bets")
    else:
        st.success(f"✅ High confidence scenario - Ready to bet")
    
    # Probability gauge chart
    fig = go.Figure(data=[go.Pie(
        labels=['Player 1', 'Player 2', 'Tie'],
        values=[prob_p1, prob_p2, prob_tie],
        hole=.3,
        marker_colors=['#2E86AB', '#A23B72', '#F18F01']
    )])
    fig.update_layout(title="Probability Distribution", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info(f"📊 Need {5 - len(st.session_state.outcomes)} more rounds for predictions. Add outcomes in the Manual Input page.")
    st.progress(0)

# Recent outcomes
st.subheader("📜 Recent Outcomes")
if st.session_state.outcomes:
    df_recent = pd.DataFrame(st.session_state.outcomes[-10:][::-1])
    st.dataframe(df_recent, use_container_width=True)
    
    # Quick stats
    total = len(st.session_state.outcomes)
    p1_total = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'P1')
    p2_total = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'P2')
    tie_total = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'TIE')
    
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Total Rounds", total)
    col_b.metric("P1 Rate", f"{p1_total/total:.1%}")
    col_c.metric("P2 Rate", f"{p2_total/total:.1%}")
    col_d.metric("TIE Rate", f"{tie_total/total:.1%}")
    
    # Streak detection
    if len(st.session_state.outcomes) >= 3:
        last_three = [o['outcome'] for o in st.session_state.outcomes[-3:]]
        if len(set(last_three)) == 1:
            st.success(f"🔥 Hot streak! Last 3 rounds all {last_three[0]}")
    
else:
    st.info("No data yet. Go to 'Manual Input' page to start recording outcomes.")

# Entropy and volatility
if len(st.session_state.outcomes) >= 20:
    st.subheader("📊 Advanced Analytics")
    
    # Calculate rolling probabilities
    df_full = pd.DataFrame(st.session_state.outcomes)
    df_full['roll_p1'] = df_full['outcome'].eq('P1').rolling(20).mean()
    df_full['roll_p2'] = df_full['outcome'].eq('P2').rolling(20).mean()
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_full.index, y=df_full['roll_p1'], name='P1 Rolling Prob', line=dict(color='#2E86AB')))
    fig2.add_trace(go.Scatter(x=df_full.index, y=df_full['roll_p2'], name='P2 Rolling Prob', line=dict(color='#A23B72')))
    fig2.update_layout(title="Rolling Probabilities (20-round window)", xaxis_title="Round", yaxis_title="Probability")
    st.plotly_chart(fig2, use_container_width=True)
