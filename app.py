import streamlit as st
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="QPIE", layout="wide")

# Initialize session state
if 'outcomes' not in st.session_state:
    st.session_state.outcomes = []
if 'cumulative_pnl' not in st.session_state:
    st.session_state.cumulative_pnl = 0.0
if 'trades' not in st.session_state:
    st.session_state.trades = []

st.title("🎲 QPIE - Probability Intelligence Engine")
st.caption("Real-time RNG Analysis & Prediction System")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Record Outcome", "🎯 Predictions", "💰 PnL Tracker", "📊 Statistics"])

# ==================== TAB 1: RECORD OUTCOME ====================
with tab1:
    st.header("Record Round Result")
    
    # Big buttons using columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏆 **PLAYER 1**\n\nWIN", use_container_width=True):
            new_outcome = {
                "round_id": len(st.session_state.outcomes) + 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "outcome": "P1"
            }
            st.session_state.outcomes.append(new_outcome)
            st.success(f"✅ Round {new_outcome['round_id']}: Player 1 Wins!")
            st.balloons()
            st.rerun()
    
    with col2:
        if st.button("🏆 **PLAYER 2**\n\nWIN", use_container_width=True):
            new_outcome = {
                "round_id": len(st.session_state.outcomes) + 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "outcome": "P2"
            }
            st.session_state.outcomes.append(new_outcome)
            st.success(f"✅ Round {new_outcome['round_id']}: Player 2 Wins!")
            st.snow()
            st.rerun()
    
    with col3:
        if st.button("⚖️ **TIE**\n\nDRAW", use_container_width=True):
            new_outcome = {
                "round_id": len(st.session_state.outcomes) + 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "outcome": "TIE"
            }
            st.session_state.outcomes.append(new_outcome)
            st.success(f"✅ Round {new_outcome['round_id']}: Tie!")
            st.balloons()
            st.rerun()
    
    st.divider()
    
    # Display recent outcomes
    st.subheader("Recent Rounds")
    if st.session_state.outcomes:
        df_recent = pd.DataFrame(st.session_state.outcomes[-10:][::-1])
        st.dataframe(df_recent, use_container_width=True)
        
        # Quick stats
        total = len(st.session_state.outcomes)
        p1_count = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'P1')
        p2_count = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'P2')
        tie_count = sum(1 for o in st.session_state.outcomes if o['outcome'] == 'TIE')
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rounds", total)
        col2.metric("P1 Wins", f"{p1_count} ({p1_count/total:.1%})")
        col3.metric("P2 Wins", f"{p2_count} ({p2_count/total:.1%})")
        col4.metric("Ties", f"{tie_count} ({tie_count/total:.1%})")
    else:
        st.info("No data yet. Click one of the buttons above to start!")

# ==================== TAB 2: PREDICTIONS ====================
with tab2:
    st.header("Next Round Probability Forecast")
    
    if len(st.session_state.outcomes) >= 5:
        # Calculate probabilities from recent history
        df = pd.DataFrame(st.session_state.outcomes)
        
        # Use last 20 rounds or all if less
        window = min(20, len(df))
        recent = df.tail(window)
        
        p1_count = recent[recent['outcome'] == 'P1'].shape[0]
        p2_count = recent[recent['outcome'] == 'P2'].shape[0]
        tie_count = recent[recent['outcome'] == 'TIE'].shape[0]
        total = len(recent)
        
        prob_p1 = p1_count / total
        prob_p2 = p2_count / total
        prob_tie = tie_count / total
        
        # Display probabilities with visual bars
        st.subheader("📊 Probability Distribution")
        
        # Player 1
        st.write(f"**Player 1:** {prob_p1:.1%}")
        st.progress(prob_p1)
        
        # Player 2
        st.write(f"**Player 2:** {prob_p2:.1%}")
        st.progress(prob_p2)
        
        # Tie
        st.write(f"**Tie:** {prob_tie:.1%}")
        st.progress(prob_tie)
        
        # Confidence calculation
        max_prob = max(prob_p1, prob_p2, prob_tie)
        
        # Adjust confidence based on data stability
        if total >= 50:
            confidence = max_prob * 0.9
        elif total >= 20:
            confidence = max_prob * 0.8
        else:
            confidence = max_prob * 0.7
        
        st.divider()
        st.subheader("🎯 Prediction Confidence")
        st.progress(confidence)
        st.caption(f"Confidence Score: {confidence:.1%}")
        
        # Trading recommendation
        if confidence >= 0.65:
            st.success(f"✅ **RECOMMENDATION: BET on {max(prob_p1, prob_p2, prob_tie, key=lambda x: {'P1': prob_p1, 'P2': prob_p2, 'TIE': prob_tie}[x])}**")
            st.caption(f"Confidence level: {confidence:.1%} exceeds threshold")
        else:
            st.warning("⚠️ **RECOMMENDATION: SKIP THIS ROUND**")
            st.caption(f"Confidence level: {confidence:.1%} below threshold. Wait for clearer pattern.")
        
        # Show historical accuracy
        st.divider()
        st.subheader("📈 Model Performance")
        
        # Simple backtest: compare predictions to actual outcomes
        if len(df) > 10:
            correct = 0
            total_backtest = 0
            for i in range(5, len(df)):
                past = df.iloc[:i]
                past_window = past.tail(min(20, len(past)))
                
                p1_past = past_window[past_window['outcome'] == 'P1'].shape[0] / len(past_window)
                p2_past = past_window[past_window['outcome'] == 'P2'].shape[0] / len(past_window)
                tie_past = past_window[past_window['outcome'] == 'TIE'].shape[0] / len(past_window)
                
                predicted = max([('P1', p1_past), ('P2', p2_past), ('TIE', tie_past)], key=lambda x: x[1])[0]
                actual = df.iloc[i]['outcome']
                
                if predicted == actual:
                    correct += 1
                total_backtest += 1
            
            if total_backtest > 0:
                accuracy = correct / total_backtest
                st.metric("Historical Prediction Accuracy", f"{accuracy:.1%}")
                st.caption(f"Based on {total_backtest} backtested rounds")
    else:
        st.info(f"📊 Need {5 - len(st.session_state.outcomes)} more rounds for predictions")
        st.caption("The system learns from patterns. More data = better predictions")

# ==================== TAB 3: PNL TRACKER ====================
with tab3:
    st.header("Profit & Loss Dashboard")
    
    # Bet size configuration
    bet_size = st.number_input("💰 Bet Size per Round ($)", min_value=1, max_value=10000, value=100, step=10)
    confidence_threshold = st.slider("Minimum Confidence to Bet", 0.5, 0.9, 0.65, step=0.05)
    
    st.divider()
    
    # Auto-calculate PnL based on recorded outcomes and predictions
    if len(st.session_state.outcomes) >= 5:
        # Calculate PnL for past rounds
        df = pd.DataFrame(st.session_state.outcomes)
        
        pnl_data = []
        cum_pnl = 0
        
        for i in range(5, len(df)):
            # Get prediction from prior data
            past = df.iloc[:i]
            window = past.tail(min(20, len(past)))
            
            p1_prob = window[window['outcome'] == 'P1'].shape[0] / len(window)
            p2_prob = window[window['outcome'] == 'P2'].shape[0] / len(window)
            tie_prob = window[window['outcome'] == 'TIE'].shape[0] / len(window)
            
            max_prob = max(p1_prob, p2_prob, tie_prob)
            confidence = max_prob * 0.8
            
            if confidence >= confidence_threshold:
                predicted = max([('P1', p1_prob), ('P2', p2_prob), ('TIE', tie_prob)], key=lambda x: x[1])[0]
                actual = df.iloc[i]['outcome']
                
                if predicted == actual:
                    if actual == 'TIE':
                        pnl = bet_size * 2.5
                    else:
                        pnl = bet_size * 0.95
                    result = "WIN"
                else:
                    pnl = -bet_size
                    result = "LOSS"
            else:
                pnl = 0
                result = "SKIPPED"
                predicted = "SKIP"
                actual = df.iloc[i]['outcome']
            
            cum_pnl += pnl
            
            pnl_data.append({
                "Round": i + 1,
                "Predicted": predicted,
                "Actual": actual,
                "Confidence": confidence,
                "PnL": pnl,
                "Cumulative": cum_pnl,
                "Result": result
            })
        
        if pnl_data:
            df_pnl = pd.DataFrame(pnl_data)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_pnl = df_pnl['PnL'].sum()
            col1.metric("Total PnL", f"${total_pnl:,.2f}", 
                       delta=f"${total_pnl:,.2f}" if total_pnl != 0 else None)
            
            trades = df_pnl[df_pnl['Result'] != 'SKIPPED']
            if len(trades) > 0:
                win_rate = (trades['Result'] == 'WIN').sum() / len(trades)
                col2.metric("Win Rate", f"{win_rate:.1%}")
                
                avg_win = trades[trades['Result'] == 'WIN']['PnL'].mean() if len(trades[trades['Result'] == 'WIN']) > 0 else 0
                avg_loss = abs(trades[trades['Result'] == 'LOSS']['PnL'].mean()) if len(trades[trades['Result'] == 'LOSS']) > 0 else 0
                
                if avg_loss > 0:
                    profit_factor = avg_win / avg_loss
                    col3.metric("Profit Factor", f"{profit_factor:.2f}")
            
            col4.metric("Total Bets", len(trades))
            
            # Recent trades table
            st.subheader("Recent Trades")
            st.dataframe(df_pnl.tail(10)[['Round', 'Predicted', 'Actual', 'Confidence', 'PnL', 'Result']].sort_values('Round', ascending=False), 
                        use_container_width=True)
            
            # Summary stats
            st.subheader("Performance Summary")
            
            total_trades = len(trades)
            if total_trades > 0:
                winning_trades = len(trades[trades['Result'] == 'WIN'])
                losing_trades = len(trades[trades['Result'] == 'LOSS'])
                skipped = len(df_pnl[df_pnl['Result'] == 'SKIPPED'])
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Winning Trades", winning_trades)
                col2.metric("Losing Trades", losing_trades)
                col3.metric("Skipped Rounds", skipped)
                
                if winning_trades + losing_trades > 0:
                    st.caption(f"Net Profit: ${total_pnl:,.2f} | Average Trade: ${df_pnl[df_pnl['Result'] != 'SKIPPED']['PnL'].mean():.2f}")
            
            # Store in session state for persistence
            st.session_state.cumulative_pnl = cum_pnl
            st.session_state.trades = pnl_data
            
        else:
            st.info("Not enough data for PnL calculation")
    else:
        st.info(f"Need {5 - len(st.session_state.outcomes)} more rounds to start PnL tracking")
        st.caption("Once you have 5+ rounds, PnL will auto-calculate based on prediction confidence")

# ==================== TAB 4: STATISTICS ====================
with tab4:
    st.header("Advanced Statistics")
    
    if len(st.session_state.outcomes) >= 10:
        df = pd.DataFrame(st.session_state.outcomes)
        
        # Streak analysis
        st.subheader("🔥 Current Streaks")
        
        if len(df) > 0:
            last_outcome = df.iloc[-1]['outcome']
            streak = 1
            for i in range(len(df)-2, -1, -1):
                if df.iloc[i]['outcome'] == last_outcome:
                    streak += 1
                else:
                    break
            
            st.metric(f"Current {last_outcome} Streak", f"{streak} in a row")
        
        # Transition matrix
        st.subheader("🔄 Transition Probabilities")
        
        transitions = {'P1': {'P1': 0, 'P2': 0, 'TIE': 0},
                      'P2': {'P1': 0, 'P2': 0, 'TIE': 0},
                      'TIE': {'P1': 0, 'P2': 0, 'TIE': 0}}
        
        for i in range(1, len(df)):
            prev = df.iloc[i-1]['outcome']
            curr = df.iloc[i]['outcome']
            transitions[prev][curr] += 1
        
        # Normalize
        for prev in transitions:
            total = sum(transitions[prev].values())
            if total > 0:
                for curr in transitions[prev]:
                    transitions[prev][curr] /= total
        
        # Display as table
        trans_df = pd.DataFrame(transitions).round(3)
        st.dataframe(trans_df, use_container_width=True)
        st.caption("Probability of transitioning from row → column")
        
        # Entropy calculation (simplified)
        st.subheader("📊 Randomness Analysis")
        
        p1_rate = (df['outcome'] == 'P1').sum() / len(df)
        p2_rate = (df['outcome'] == 'P2').sum() / len(df)
        tie_rate = (df['outcome'] == 'TIE').sum() / len(df)
        
        # Shannon entropy
        import math
        entropy = 0
        for p in [p1_rate, p2_rate, tie_rate]:
            if p > 0:
                entropy -= p * math.log2(p)
        
        max_entropy = math.log2(3)
        normalized_entropy = entropy / max_entropy
        
        col1, col2 = st.columns(2)
        col1.metric("Shannon Entropy", f"{entropy:.3f} bits")
        col2.metric("Normalized Entropy", f"{normalized_entropy:.1%}")
        
        if normalized_entropy < 0.8:
            st.warning("⚠️ Low entropy detected - outcomes may not be fully random")
        else:
            st.success("✅ Entropy within expected range")
        
        # Volatility
        st.subheader("📈 Rolling Volatility")
        
        rolling_p1 = df['outcome'].eq('P1').rolling(10).mean().dropna()
        volatility = rolling_p1.std()
        st.metric("10-Round Volatility Index", f"{volatility:.3f}")
        
        if volatility > 0.3:
            st.warning("⚠️ High volatility - unpredictable patterns")
        else:
            st.info(f"Stable patterns detected")
        
    else:
        st.info(f"Need {10 - len(st.session_state.outcomes)} more rounds for advanced statistics")

# Sidebar with overall stats
with st.sidebar:
    st.header("📊 Overall Statistics")
    st.metric("Total Rounds", len(st.session_state.outcomes))
    
    if len(st.session_state.outcomes) > 0:
        df_side = pd.DataFrame(st.session_state.outcomes)
        p1 = (df_side['outcome'] == 'P1').sum() / len(df_side)
        p2 = (df_side['outcome'] == 'P2').sum() / len(df_side)
        tie = (df_side['outcome'] == 'TIE').sum() / len(df_side)
        
        st.metric("P1 Win Rate", f"{p1:.1%}")
        st.metric("P2 Win Rate", f"{p2:.1%}")
        st.metric("Tie Rate", f"{tie:.1%}")
    
    st.divider()
    st.caption("QPIE - Probability Intelligence Engine")
    st.caption("Real-time RNG Analysis & Prediction")
    
    if st.button("🔄 Reset All Data", type="secondary"):
        st.session_state.outcomes = []
        st.session_state.trades = []
        st.session_state.cumulative_pnl = 0.0
        st.success("All data cleared!")
        st.rerun()
