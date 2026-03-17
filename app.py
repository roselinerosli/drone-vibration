import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Drone Diagnostics", layout="wide", page_icon="🚁")

# 2. ANIMATED BACKGROUND (Flying Drones)
st.markdown("""
    <style>
    /* Global Background */
    .stApp { background: linear-gradient(to bottom right, #f4f8fc, #ffffff); }
    
    /* THE DRONE CONTAINER */
    .drone-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden;
    }
    
    /* BASE DRONE STYLING */
    .drone {
        position: absolute; display: block; filter: grayscale(50%);
    }

    /* DRONE FLEET SETUP (Size, Opacity, Start Position, Animation Speed) */
    /* Flying Right (Flipped using scaleX) */
    .d1 { top: 10%; left: -10%; font-size: 25px; opacity: 0.3; animation: flyRight 35s linear infinite; }
    .d2 { top: 40%; left: -15%; font-size: 45px; opacity: 0.15; animation: flyRight 25s linear infinite 5s; }
    .d3 { top: 70%; left: -10%; font-size: 20px; opacity: 0.4; animation: flyRight 40s linear infinite 12s; }
    .d4 { top: 85%; left: -20%; font-size: 60px; opacity: 0.1; animation: flyRight 20s linear infinite 2s; }

    /* Flying Left (Normal emoji orientation) */
    .d5 { top: 20%; right: -10%; font-size: 30px; opacity: 0.25; animation: flyLeft 28s linear infinite 3s; }
    .d6 { top: 55%; right: -15%; font-size: 50px; opacity: 0.15; animation: flyLeft 22s linear infinite 8s; }
    .d7 { top: 80%; right: -10%; font-size: 25px; opacity: 0.35; animation: flyLeft 32s linear infinite 1s; }
    .d8 { top: 30%; right: -20%; font-size: 70px; opacity: 0.08; animation: flyLeft 18s linear infinite 15s; }

    /* --- FLIGHT ANIMATIONS WITH BOBBING --- */
    @keyframes flyRight {
        0%   { transform: translate(0vw, 0px) scaleX(-1) rotate(-5deg); }
        25%  { transform: translate(35vw, -30px) scaleX(-1) rotate(2deg); }
        50%  { transform: translate(70vw, 20px) scaleX(-1) rotate(-2deg); }
        75%  { transform: translate(105vw, -15px) scaleX(-1) rotate(5deg); }
        100% { transform: translate(130vw, 0px) scaleX(-1) rotate(-5deg); }
    }

    @keyframes flyLeft {
        0%   { transform: translate(0vw, 0px) rotate(5deg); }
        25%  { transform: translate(-35vw, 30px) rotate(-2deg); }
        50%  { transform: translate(-70vw, -20px) rotate(2deg); }
        75%  { transform: translate(-105vw, 15px) rotate(-5deg); }
        100% { transform: translate(-130vw, 0px) rotate(5deg); }
    }

    /* EXISTING QUAD-COLOR THEME */
    div[data-testid="column"] {
        padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); 
        border: none; z-index: 1; position: relative;
    }
    div[data-testid="column"]:nth-of-type(1) { background-color: rgba(227, 242, 253, 0.95); color: #0d47a1; }
    div[data-testid="column"]:nth-of-type(2) { background-color: rgba(224, 247, 250, 0.95); }
    div[data-testid="column"]:nth-of-type(3) { background-color: rgba(232, 234, 246, 0.95); }
    div[data-testid="column"]:nth-of-type(4) { background-color: rgba(236, 239, 241, 0.95); }

    .safe-status { color: #004d40; background-color: #b2dfdb; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; border: 2px solid #004d40;}
    @keyframes blinker { 50% { opacity: 0.3; } }
    .blinking { animation: blinker 0.8s linear infinite; color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; border: 2px solid #721c24; }
    </style>
    
    <div class="drone-bg">
        <div class="drone d1">🚁</div>
        <div class="drone d2">🚁</div>
        <div class="drone d3">🚁</div>
        <div class="drone d4">🚁</div>
        <div class="drone d5">🚁</div>
        <div class="drone d6">🚁</div>
        <div class="drone d7">🚁</div>
        <div class="drone d8">🚁</div>
    </div>
    """, unsafe_allow_html=True)

st.title("🚁 Drone Vibration Analysis System")

# Layout
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

if 'df' not in st.session_state:
    st.session_state.df = None

# ==========================================
# SECTION 1: AUTOMATED DATA INPUT
# ==========================================
with col1:
    st.subheader("1. Flight Data Input")
    uploaded_file = st.file_uploader("Upload CSV (Raw, G_Force)", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # 1. Read the 2-column CSV (Raw, G_Force)
            df_raw = pd.read_csv(uploaded_file)
            
            # Extract just the first two columns to be safe, rename them for the app
            df = pd.DataFrame()
            df["Raw"] = df_raw.iloc[:, 0]
            df["Accel"] = df_raw.iloc[:, 1]
            
            # 2. Force limit to exactly 1024 rows
            if len(df) > 1024:
                df = df.head(1024)
            
            # 3. Automatically generate Index (0 to 1023)
            df.insert(0, "Index", np.arange(len(df)))
            
            # 4. Automatically generate Time (Assumes 100Hz -> 0.01s steps)
            T_interval = 0.01
            df.insert(1, "Time", df["Index"] * T_
