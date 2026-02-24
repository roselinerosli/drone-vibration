import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Drone Diagnostics", layout="wide", page_icon="🚁")

# 2. CUSTOM CSS (4 Distinct Aesthetic Colors)
st.markdown("""
    <style>
    /* Global Background - Clean White */
    .stApp { background-color: #aed3e3; }
    
    /* General Card Styling */
    div[data-testid="column"] {
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
        border: none; 
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
            sampling_rate = 1.0 / T
            
            # Store
            st.session_state.df = df
            st.session_state.N = N
            st.session_state.T = T
            st.session_state.rate = sampling_rate
            
            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Samples", f"{N}")
            m2.metric("Interval", f"{T:.3f} s")
            m3.metric("Rate", f"{int(sampling_rate)} Hz")
            
            st.success("✅ Data Loaded Successfully")
            
        except Exception as e:
            st.error(f"Error reading file: {e}")

# ==========================================
# SECTION 2: FFT ANALYSIS (Minty Azure)
# ==========================================
with col2:
    st.subheader("2. Frequency Analysis (FFT)")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        N = st.session_state.N
        T = st.session_state.T
        
        # FFT Math (Exact Excel Formula)
        dft_coeffs = np.fft.fft(df["Accel"])
        spectral_amplitude = np.abs(dft_coeffs) * (2.0 / N)
        
        k_indices = np.arange(N)
        frequency_hz = k_indices * (1.0 / (N * T))
        
        # Slicing
        half_N = N // 2
        final_freq = frequency_hz[:half_N]
        final_amp = spectral_amplitude[:half_N]
        final_amp[0] = 0 # Zero DC Offset
        
        # Graphing
        fft_df = pd.DataFrame({"Frequency": final_freq, "Spectral Amplitude": final_amp})
        
        peak_idx = np.argmax(final_amp)
        peak_freq = final_freq[peak_idx]
        peak_mag = final_amp[peak_idx]
        
        peak_data = pd.DataFrame({
            "Frequency": [peak_freq], 
            "Spectral Amplitude": [peak_mag], 
            "Label": [f"Peak: {peak_freq:.1f} Hz"]
        })

        # Deep Ocean Blue Graph Line
        line_chart = alt.Chart(fft_df).mark_line(color='#0277bd').encode( 
            x=alt.X('Frequency', title='Frequency (Hz)'),
            y=alt.Y('Spectral Amplitude', title='Spectral Amplitude (G)'),
            tooltip=['Frequency', 'Spectral Amplitude']
        )
        peak_point = alt.Chart(peak_data).mark_circle(color='#d32f2f', size=100).encode( 
            x='Frequency', y='Spectral Amplitude', tooltip=['Label', 'Spectral Amplitude']
        )
        st.altair_chart((line_chart + peak_point).interactive(), use_container_width=True)

# ==========================================
# SECTION 3: REFERENCE GUIDE (Pale Indigo)
# ==========================================
with col3:
    st.subheader("3. Failure Reference Guide")
    
    # Aesthetic Minimalist Table
    st.markdown("""
    <div style="font-size: 13px; color: #444;">
    <table style="width:100%; border-collapse: collapse; background-color: rgba(255,255,255,0.4); border-radius: 8px;">
      <tr style="border-bottom: 2px solid #145374;">
        <th style="text-align: left; padding: 8px; color: #3949ab;">Range</th>
        <th style="text-align: left; padding: 8px; color: #3949ab;">Condition</th>
        <th style="text-align: left; padding: 8px; color: #3949ab;">Status</th>
      </tr>
      <tr style="border-bottom: 1px solid #5588a3;">
        <td style="padding: 6px;">0 - 5 Hz</td>
        <td style="padding: 6px;">Normal / Wind</td>
        <td style="padding: 6px; color: #2e7d32; font-weight: bold;">🟢 Safe</td>
      </tr>
      <tr style="border-bottom: 1px solid #e8e8e8;">
        <td style="padding: 6px;">5 - 10 Hz</td>
        <td style="padding: 6px;">Propeller Imbalance</td>
        <td style="padding: 6px; color: #f9a825; font-weight: bold;">🟡 Check</td>
      </tr>
      <tr style="border-bottom: 1px solid #00334e;">
        <td style="padding: 6px;">10 - 20 Hz</td>
        <td style="padding: 6px;">Bent Shaft</td>
        <td style="padding: 6px; color: #ef6c00; font-weight: bold;">🟠 Danger</td>
      </tr>
      <tr>
        <td style="padding: 6px;">20+ Hz</td>
        <td style="padding: 6px;">Bad Bearings</td>
        <td style="padding: 6px; color: #c62828; font-weight: bold;">🔴 Critical</td>
      </tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# SECTION 4: DIAGNOSTICS ALERT (Mist Grey-Blue)
# ==========================================
with col4:
    st.subheader("4. System Health Status")
    
    if st.session_state.df is not None:
        st.write(f"**Max Vibration:** {peak_mag:.4f} G at **{peak_freq:.2f} Hz**")
        st.write("---")
        
        # --- STRICT FREQUENCY LOGIC ---
        
        # 0 to 5 Hz: SAFE
        if peak_freq <= 5:
            st.markdown('<div class="safe-status">✅ SYSTEM NORMAL</div>', unsafe_allow_html=True)
            st.write(f"Peak at {peak_freq:.2f} Hz is within the safe range (0-5 Hz).")
            
        # 5 to 10 Hz: PROP IMBALANCE
        elif 5 < peak_freq <= 10:
            st.markdown('<div class="blinking">⚠️ PROP IMBALANCE</div>', unsafe_allow_html=True)
            st.info(f"**Warning:** Peak detected at {peak_freq:.2f} Hz.")
            st.markdown("**🛠 Fix:** Check props for chips. Tighten prop nuts.")
            
        # 10 to 20 Hz: SHAFT ISSUE
        elif 10 < peak_freq <= 20:
            st.markdown('<div class="blinking">🟠 MOTOR SHAFT ISSUE</div>', unsafe_allow_html=True)
            st.warning(f"**Danger:** Peak detected at {peak_freq:.2f} Hz.")
            st.markdown("**🛠 Fix:** Remove props. Spin motors manually. Check for wobble.")
            
        # Above 20 Hz: BEARING FAILURE
        else:
            st.markdown('<div class="blinking">🔴 BEARING FAILURE</div>', unsafe_allow_html=True)
            st.error(f"**Critical:** High frequency peak at {peak_freq:.2f} Hz.")
            st.markdown("**🛠 Fix:** Grinding sound? Replace motor immediately.")
