import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Input", layout="centered")

st.title("📝 Record Round Outcome")

# CSS for big buttons
st.markdown("""
<style>
.stButton > button {
    width: 100%;
    height: 100px;
    font-size: 24px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Initialize
if 'outcomes' not in st.session_state:
    st.session_state.outcomes = []

def add_outcome(outcome):
    new = {
        "round": len(st.session_state.outcomes) + 1,
        "time": datetime.now().strftime("%H:%M:%S"),
        "outcome": outcome
    }
    st.session_state.outcomes.append(new)
    st.success(f"✅ Round {new['round']}: {outcome}")
    st.balloons()
    st.rerun()

# Three buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏆 P1", use_container_width=True):
        add_outcome("P1")

with col2:
    if st.button("🏆 P2", use_container_width=True):
        add_outcome("P2")

with col3:
    if st.button("⚖️ TIE", use_container_width=True):
        add_outcome("TIE")

# Show history
st.divider()
if st.session_state.outcomes:
    df = pd.DataFrame(st.session_state.outcomes[-10:][::-1])
    st.dataframe(df, use_container_width=True)
