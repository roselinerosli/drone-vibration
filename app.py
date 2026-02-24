import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Drone Diagnostics", layout="wide", page_icon="🚁")

# 2. CUSTOM CSS (4 Distinct Aesthetic Colors)
st.markdown("""
    <style>
    /* Global Background - Clean White to let sections pop */
    .stApp { background-color: #ffffff; }
    
    /* General Card Styling */
    div[data-testid="column"] {
        padding: 20px; 
        border-radius: 15px; /* Softer rounded corners */
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); /* Floating effect */
        border: none; /* Removed border for cleaner look */
    }
    
    /* --- THE 4 DISTINCT SECTIONS --- */
    
    /* 1. Top Left: Soft Cloud Blue */
    div[data-testid="column"]:nth-of-type(1) { 
        background-color: #e3f2fd; 
        color: #0d47a1;
    }
    
    /* 2. Top Right: Minty Azure */
    div[data-testid="column"]:nth-of-type(2) { 
        background-color: #e0f7fa; 
    }
    
    /* 3. Bottom Left: Pale Indigo */
    div[data-testid="column"]:nth-of-type(3) { 
        background-color: #e8eaf6; 
    }
    
    /* 4. Bottom Right: Mist Grey-Blue */
    div[data-testid="column"]:nth-of-type(4) { 
        background-color: #eceff1; 
    }

    /* ------------------------------ */

    /* Blinking Animation for Critical Warnings */
    @keyframes blinker { 50% { opacity: 0.3; } }
    .blinking {
        animation: blinker 0.8s linear infinite; 
        color: #721c24; 
        background-color: #f8d7da;
        padding: 10px; border-radius: 8px; 
        text-align: center; font-weight: bold; 
        border: 2px solid #721c24;
    }
    
    /* Safe Status Style */
    .safe-status {
        color: #004d40; 
        background-color: #b2dfdb; 
        padding: 10px; border-radius: 8px; 
        text-align: center; font-weight: bold; 
        border: 2px solid #004d40;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 Drone Vibration Analysis System")

# Layout
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

if 'df' not in st.session_state:
    st.session_state.df = None

# ==========================================
# SECTION 1: DATA INPUT (Cloud Blue)
# ==========================================
with col1:
    st.subheader("1. Flight Data Input")
    uploaded_file = st.file_uploader("Upload CSV (Index, Time, Raw, Accel)", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # READ 4 COLUMNS
            df = pd.read_csv(uploaded_file, header=None, names=["Index", "Time", "Raw", "Accel"])
            
            # Metadata
            N = len(df)
            T = df["Time"].iloc[1] - df["Time"].iloc[0]
            if T == 0: T = 0.01 
            sampling_rate =
