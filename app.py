import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Drone Diagnostics", layout="wide", page_icon="🚁")

# 2. CUSTOM CSS FOR STYLING
# This hides the default top padding and creates "cards" for each section
st.markdown("""
    <style>
    /* Main background color */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Style for the 4 distinct sections (Cards) */
    .css-1r6slb0 {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Blinking Animation for Critical Warnings */
    @keyframes blinker {
        50% { opacity: 0; }
    }
    .blinking {
        animation: blinker 1s linear infinite;
        color: #ff4b4b;
        font-weight: bold;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 Drone Vibration Analysis System")

# Create the 2x2 Grid Layout
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# ==========================================
# SECTION 1: DATA METRICS (Top Left)
# ==========================================
with col1:
    st.subheader("1. Flight Data Metadata")
    uploaded_file = st.file_uploader("Upload VIBRATE.CSV", type=["csv"])
    
    if uploaded_file is not None:
        # Read Data
        df = pd.read_csv(uploaded_file, header=None, names=["Raw", "G_Force"])
        
        # Calculate Engineering Metrics
        N = len(df)                 # Total Samples
        T = 0.01                    # Interval (10ms)
        duration = N * T            # Total seconds
        sampling_rate = 1 / T       # Hz (100 Hz)
        
        # Display Metrics using neat Streamlit columns
        m1, m2, m3 = st.columns(3)
        m1.metric("Sample Count", f"{N}")
        m2.metric("Duration", f"{duration:.2f} s")
        m3.metric("Sampling Rate", f"{int(sampling_rate)} Hz")
        
        st.info(f"✅ Data loaded successfully. Interval: {T}s")

# ==========================================
# SECTION 2: FFT GRAPH WITH PEAK MARKER (Top Right)
# ==========================================
with col2:
    st.subheader("2. Frequency Domain Analysis")
    
    if uploaded_file is not None:
        # --- FFT CALCULATIONS ---
        yf = np.fft.fft(df["G_Force"])
        xf = np.fft.fftfreq(N, T)[:N//2]
        magnitude = 2.0/N * np.abs(yf[0:N//2])
        magnitude[0] = 0  # Remove DC offset
        
        # Find Peak
        peak_idx = np.argmax(magnitude)
        peak_freq = xf[peak_idx]
        peak_mag = magnitude[peak_idx]
        
        # --- PLOTTING WITH MATPLOTLIB ---
        fig, ax = plt.subplots(figsize=(6, 4))
        
        # Plot the blue line
        ax.plot(xf, magnitude, label="Vibration Spectrum", color="#0068c9")
        
        # Plot the RED DOT at the peak
        ax.scatter(peak_freq, peak_mag, color="red", s=100, zorder=5, label="Max Peak")
        
        # Add labels and grid
        ax.set_title(f"Peak Detected at {peak_freq:.1f} Hz", fontsize=10)
        ax.set_xlabel("Frequency (Hz)", fontsize=9)
        ax.set_ylabel("Magnitude (G)", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
        
        # Show in Streamlit
        st.pyplot(fig)

# ==========================================
# SECTION 3: REFERENCE GUIDE (Bottom Left)
# ==========================================
with col3:
    st.subheader("3. Failure Mode Reference")
    st.markdown("""
    <div style="background-color: white; padding: 10px; border-radius: 5px;">
    
    | Frequency Range | Probable Cause | Severity |
    | :--- | :--- | :--- |
    | **0 - 10 Hz** | Control Inputs / Wind Buffeting | 🟢 Low |
    | **10 - 40 Hz** | **Propeller Imbalance** | 🟡 Medium |
    | **40 - 90 Hz** | **Bent Motor Shaft / Bell** | 🟠 High |
    | **100+ Hz** | **Motor Bearing Failure** | 🔴 Critical |
    
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# SECTION 4: DIAGNOSTICS & ACTION PLAN (Bottom Right)
# ==========================================
with col4:
    st.subheader("4. Automated Diagnosis")
    
    if uploaded_file is not None:
        # Display the Main Result
        st.write(f"**Peak Frequency:** {peak_freq:.2f} Hz")
        st.write(f"**Vibration Intensity:** {peak_mag:.2f} G")
        
        st.divider() # Draws a line
        
        # LOGIC ENGINE
        if peak_mag < 0.15:
            st.success("✅ **SYSTEM HEALTHY**")
            st.write("Vibration levels are within normal operating limits.")
            
        elif 10 <= peak_freq <= 40:
            st.warning("⚠️ **WARNING: PROPELLER ISSUE**")
            st.markdown("### 🛠 Recommended Actions:")
            st.markdown("""
            * **Inspect Props:** Check for chips, cracks, or bends.
            * **Balance Props:** Use a prop balancer tool.
            * **Check Hubs:** Ensure prop nuts are tightened securely.
            """)
            
        elif 40 < peak_freq <= 90:
            st.error("🚨 **DANGER: MOTOR SHAFT ISSUE**")
            st.markdown('<p class="blinking">CRITICAL VIBRATION DETECTED</p>', unsafe_allow_html=True)
            st.markdown("### 🛠 Recommended Actions:")
            st.markdown("""
            * **Remove Props:** Spin motors manually to check for wobble.
            * **Inspect Bell:** Look for dents on the motor bell.
            * **Replace Shaft:** If the shaft is bent, replace the motor immediately.
            """)
            
        elif peak_freq > 90:
            st.error("🚨 **DANGER: BEARING FAILURE**")
            st.markdown('<p class="blinking">HIGH FREQUENCY RESONANCE</p>', unsafe_allow_html=True)
            st.markdown("### 🛠 Recommended Actions:")
            st.markdown("""
            * **Listen:** Spin motor by hand; listen for "gritty" sounds.
            * **Feel:** Check for excessive heat after flight.
            * **Replace:** Bearings are likely shot. Do not fly.
            """)
    else:
        st.info("Waiting for data...")
