import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Drone Diagnostics", layout="wide", page_icon="🚁")

# 2. CUSTOM CSS
st.markdown("""
    <style>
    .stApp { background-color: #fdfbf7; }
    div[data-testid="column"] {
        padding: 20px; border: 2px solid #2c2c2c; border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    div[data-testid="column"]:nth-of-type(1) { background-color: #f5f5dc; }
    div[data-testid="column"]:nth-of-type(2) { background-color: #faf0e6; }
    div[data-testid="column"]:nth-of-type(3) { background-color: #fff8dc; }
    div[data-testid="column"]:nth-of-type(4) { background-color: #faebd7; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .blinking {
        animation: blinker 0.8s linear infinite; color: #721c24; background-color: #f8d7da;
        padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; border: 2px solid #721c24;
    }
    .safe-status {
        color: #155724; background-color: #d4edda; padding: 10px; border-radius: 5px;
        text-align: center; font-weight: bold; border: 2px solid #155724;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 Drone Vibration Analysis System")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

if 'df' not in st.session_state:
    st.session_state.df = None

# ==========================================
# SECTION 1: DATA INPUT (Recalculate from Raw)
# ==========================================
with col1:
    st.subheader("1. Flight Data Input")
    uploaded_file = st.file_uploader("Upload CSV (Time, Raw, G-Force)", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Read all 3 columns
            df = pd.read_csv(uploaded_file, header=None, names=["Time", "Raw", "G_Ref"])
            
            # --- CRITICAL FIX: RECALCULATE FROM RAW ---
            # We ignore the rounded 'G_Ref' column and calculate fresh float values
            # Using standard ADXL335 Sensitivity (67 units = 1G)
            ZERO_OFFSET = 349  # Midpoint (from your data)
            SENSITIVITY = 67.0 
            
            df["G_Force"] = (df["Raw"] - ZERO_OFFSET) / SENSITIVITY
            
            # Metrics
            N = len(df)
            duration = df["Time"].iloc[-1] - df["Time"].iloc[0]
            sampling_rate = N / duration if duration > 0 else 100
            
            st.session_state.df = df
            st.session_state.N = N
            st.session_state.rate = sampling_rate
            
            # Display Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Samples", f"{N}")
            m2.metric("Duration", f"{duration:.2f} s")
            m3.metric("Rate", f"{int(sampling_rate)} Hz")
            
            st.caption(f"✅ Data Processed. Re-calculated precision from Raw Data.")
            
        except Exception as e:
            st.error(f"Error reading file: {e}")

# ==========================================
# SECTION 2: FFT ANALYSIS (Matches Excel Formula)
# ==========================================
with col2:
    st.subheader("2. Frequency Analysis (FFT)")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        N = st.session_state.N
        rate = st.session_state.rate
        
        # --- FFT CALCULATION ---
        # This matches Excel's =IMABS() * (2/N)
        T = 1.0 / rate
        yf = np.fft.fft(df["G_Force"])
        xf = np.fft.fftfreq(N, T)[:N//2]
        magnitude = 2.0/N * np.abs(yf[0:N//2])
        
        # Zero out the DC Offset (0Hz) so it doesn't skew the graph
        magnitude[0] = 0 
        
        # Altair Graph
        fft_df = pd.DataFrame({"Frequency": xf, "Magnitude": magnitude})
        peak_idx = np.argmax(magnitude)
        peak_freq = xf[peak_idx]
        peak_mag = magnitude[peak_idx]
        
        peak_data = pd.DataFrame({"Frequency": [peak_freq], "Magnitude": [peak_mag], "Label": [f"Peak: {peak_freq:.1f} Hz"]})

        line_chart = alt.Chart(fft_df).mark_line(color='#4e342e').encode(
            x=alt.X('Frequency', title='Frequency (Hz)'),
            y=alt.Y('Magnitude', title='Magnitude (G)'),
            tooltip=['Frequency', 'Magnitude']
        )
        peak_point = alt.Chart(peak_data).mark_circle(color='red', size=100).encode(
            x='Frequency', y='Magnitude', tooltip=['Label', 'Magnitude']
        )
        st.altair_chart((line_chart + peak_point).interactive(), use_container_width=True)

# ==========================================
# SECTION 3: REFERENCE GUIDE
# ==========================================
with col3:
    st.subheader("3. Failure Reference Guide")
    st.markdown("""
    | Frequency | Condition | Status |
    | :--- | :--- | :--- |
    | **0 - 10 Hz** | Normal Flight / Wind | 🟢 Safe |
    | **10 - 40 Hz** | **Propeller Imbalance** | 🟡 Check |
    | **40 - 90 Hz** | **Bent Shaft / Loose Motor** | 🟠 Danger |
    | **100+ Hz** | **Bad Bearings** | 🔴 Critical |
    """)

# ==========================================
# SECTION 4: DIAGNOSTICS
# ==========================================
with col4:
    st.subheader("4. System Health Status")
    
    if st.session_state.df is not None:
        st.write(f"**Max Vibration:** {peak_mag:.3f} G at **{peak_freq:.2f} Hz**")
        st.write("---")
        
        if peak_mag < 0.2:
            st.markdown('<div class="safe-status">✅ SYSTEM NORMAL</div>', unsafe_allow_html=True)
            st.write("Vibration levels are minimal.")
        elif 10 <= peak_freq <= 40:
            st.markdown('<div class="blinking">⚠️ PROP IMBALANCE</div>', unsafe_allow_html=True)
            st.info("💡 **Fix:** Check props for chips. Tighten prop nuts.")
        elif 40 < peak_freq <= 90:
            st.markdown('<div class="blinking">🟠 MOTOR SHAFT ISSUE</div>', unsafe_allow_html=True)
            st.warning("💡 **Fix:** Remove props. Spin motors. Check for wobble.")
        elif peak_freq > 90:
            st.markdown('<div class="blinking">🔴 BEARING FAILURE</div>', unsafe_allow_html=True)
            st.error("💡 **Fix:** Grinding sound? Replace motor immediately.")
