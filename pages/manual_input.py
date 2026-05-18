 import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

st.set_page_config(page_title="Manual Outcome Input", layout="centered")

st.title("🎮 Manual Outcome Entry")
st.markdown("### Click the button for the round result")

# Add custom CSS for bigger buttons
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        height: 120px;
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'outcomes' not in st.session_state:
    # Try to load existing data
    persistent_path = os.path.join(os.path.expanduser("~"), ".streamlit", "outcomes.csv")
    if os.path.exists(persistent_path):
        df = pd.read_csv(persistent_path)
        st.session_state.outcomes = df.to_dict('records')
    else:
        st.session_state.outcomes = []

# Function to save data persistently
def save_outcomes():
    if st.session_state.outcomes:
        df = pd.DataFrame(st.session_state.outcomes)
        # Save to persistent location
        persistent_path = os.path.join(os.path.expanduser("~"), ".streamlit", "outcomes.csv")
        os.makedirs(os.path.dirname(persistent_path), exist_ok=True)
        df.to_csv(persistent_path, index=False)

# Function to add outcome
def add_outcome(outcome):
    new_round = {
        "round_id": len(st.session_state.outcomes) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "outcome": outcome
    }
    st.session_state.outcomes.append(new_round)
    save_outcomes()
    
    st.success(f"✅ Round {new_round['round_id']} recorded: {outcome}")
    st.balloons()
    
    # Force a rerun to update main page
    st.rerun()

# Three main buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏆 **P1 WINS**", use_container_width=True, key="p1_btn"):
        add_outcome("P1")

with col2:
    if st.button("🏆 **P2 WINS**", use_container_width=True, key="p2_btn"):
        add_outcome("P2")

with col3:
    if st.button("⚖️ **TIE**", use_container_width=True, key="tie_btn"):
        add_outcome("TIE")

st.divider()

# Show prediction for next round
st.subheader("🔮 Next Round Prediction")

if len(st.session_state.outcomes) >= 5:
    df = pd.DataFrame(st.session_state.outcomes)
    recent = df.tail(20)
    
    p1_count = recent[recent['outcome'] == 'P1'].shape[0]
    p2_count = recent[recent['outcome'] == 'P2'].shape[0]
    tie_count = recent[recent['outcome'] == 'TIE'].shape[0]
    total = len(recent)
    
    prob_p1 = p1_count / total
    prob_p2 = p2_count / total
    prob_tie = tie_count / total
    
    # Display with metrics
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("🎯 P1 Probability", f"{prob_p1:.1%}", 
                 delta=f"{prob_p1 - 0.333:.1%}" if prob_p1 != 0.333 else None)
    col_b.metric("🎯 P2 Probability", f"{prob_p2:.1%}",
                 delta=f"{prob_p2 - 0.333:.1%}" if prob_p2 != 0.333 else None)
    col_c.metric("🎯 TIE Probability", f"{prob_tie:.1%}",
                 delta=f"{prob_tie - 0.334:.1%}" if prob_tie != 0.334 else None)
    
    # Confidence calculation
    max_prob = max(prob_p1, prob_p2, prob_tie)
    confidence = max_prob * 0.8
    
    st.progress(confidence)
    st.caption(f"Confidence Score: {confidence:.1%}")
    
    # Recommendation
    col_x, col_y = st.columns(2)
    with col_x:
        if confidence > 0.65:
            st.success("✅ **RECOMMENDATION: BET**")
            st.caption("High confidence scenario detected")
        else:
            st.warning("⚠️ **RECOMMENDATION: SKIP**")
            st.caption("Low confidence - wait for clearer pattern")
    
    with col_y:
        if st.button("⏭️ Skip This Round (Record No Bet)", use_container_width=True):
            st.info("Round skipped. No impact on PnL.")
            skip_record = {
                "round_id": len(st.session_state.outcomes) + 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "outcome": "SKIPPED",
                "reason": "Low confidence"
            }
            # Optionally track skips
            if 'skips' not in st.session_state:
                st.session_state.skips = []
            st.session_state.skips.append(skip_record)
            st.rerun()
    
else:
    st.info(f"📊 Need {5 - len(st.session_state.outcomes)} more rounds for predictions")
    st.caption("The system learns from patterns. More data = better predictions")

# Display history
st.divider()
st.subheader("📜 Round History")

if st.session_state.outcomes:
    df_history = pd.DataFrame(st.session_state.outcomes[-20:][::-1])
    st.dataframe(df_history, use_container_width=True)
    
    # Statistics
    total = len(st.session_state.outcomes)
    p1_total = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'P1')
    p2_total = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'P2')
    tie_total = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'TIE')
    
    st.caption(f"📊 All-time stats: P1={p1_total} ({p1_total/total:.1%}) | P2={p2_total} ({p2_total/total:.1%}) | TIE={tie_total} ({tie_total/total:.1%})")
    
    # Display last outcome with animation
    last_outcome = st.session_state.outcomes[-1]['outcome']
    if last_outcome == 'P1':
        st.balloons()
    elif last_outcome == 'P2':
        st.snow()
        
else:
    st.info("📭 No data yet. Click one of the buttons above to start!")
    st.caption("The system will begin learning patterns immediately")

# Clear data button (admin)
st.divider()
if st.checkbox("⚠️ Admin Options"):
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.outcomes = []
        save_outcomes()
        st.warning("All data cleared!")
        st.rerun()
