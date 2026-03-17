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
            df.insert(1, "Time", df["Index"] * T_interval)
            
            # Metadata
            N = len(df)
            T = T_interval
            sampling_rate = 1.0 / T
            
            # Store in session state
            st.session_state.df = df
            st.session_state.N = N
            st.session_state.T = T
            st.session_state.rate = sampling_rate
            
            # Metrics Display
            m1, m2, m3 = st.columns(3)
            m1.metric("Samples Used", f"{N}")
            m2.metric("Calculated Duration", f"{(N-1)*T:.2f} s")
            m3.metric("Assumed Rate", f"{int(sampling_rate)} Hz")
            
            st.success("✅ Data Cleaned: 1024 rows truncated, Time & Index auto-generated.")
            
        except Exception as e:
            st.error(f"Error reading or processing file: {e}")

# ==========================================
# SECTION 2: FFT ANALYSIS
# ==========================================
with col2:
    st.subheader("2. Frequency Analysis (FFT)")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        N = st.session_state.N
        T = st.session_state.T
        
        # FFT Math
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
# SECTION 3: REFERENCE GUIDE
# ==========================================
with col3:
    st.subheader("3. Failure Reference Guide")
    
    st.markdown("""
    <div style="font-size: 13px; color: #444;">
    <table style="width:100%; border-collapse: collapse; background-color: rgba(255,255,255,0.4); border-radius: 8px;">
      <tr style="border-bottom: 2px solid #5c6bc0;">
        <th style="text-align: left; padding: 8px; color: #3949ab;">Range</th>
        <th style="text-align: left; padding: 8px; color: #3949ab;">Condition</th>
        <th style="text-align: left; padding: 8px; color: #3949ab;">Status</th>
      </tr>
      <tr style="border-bottom: 1px solid #e8eaf6;">
        <td style="padding: 6px;">0 - 5 Hz</td>
        <td style="padding: 6px;">Normal / Wind</td>
        <td style="padding: 6px; color: #2e7d32; font-weight: bold;">🟢 Safe</td>
      </tr>
      <tr style="border-bottom: 1px solid #e8eaf6;">
        <td style="padding: 6px;">5 - 10 Hz</td>
        <td style="padding: 6px;">Propeller Imbalance</td>
        <td style="padding: 6px; color: #f9a825; font-weight: bold;">🟡 Check</td>
      </tr>
      <tr style="border-bottom: 1px solid #e8eaf6;">
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
# SECTION 4: DIAGNOSTICS ALERT
# ==========================================
with col4:
    st.subheader("4. System Health Status")
    
    if st.session_state.df is not None:
        st.write(f"**Max Vibration:** {peak_mag:.4f} G at **{peak_freq:.2f} Hz**")
        st.write("---")
        
        if peak_freq <= 5:
            st.markdown('<div class="safe-status">✅ SYSTEM NORMAL</div>', unsafe_allow_html=True)
            st.write(f"Peak at {peak_freq:.2f} Hz is within the safe range (0-5 Hz).")
        elif 5 < peak_freq <= 10:
            st.markdown('<div class="blinking">⚠️ PROP IMBALANCE</div>', unsafe_allow_html=True)
            st.info(f"**Warning:** Peak detected at {peak_freq:.2f} Hz.")
            st.markdown("**🛠 Fix:** Check props for chips. Tighten prop nuts.")
        elif 10 < peak_freq <= 20:
            st.markdown('<div class="blinking">🟠 MOTOR SHAFT ISSUE</div>', unsafe_allow_html=True)
            st.warning(f"**Danger:** Peak detected at {peak_freq:.2f} Hz.")
            st.markdown("**🛠 Fix:** Remove props. Spin motors manually. Check for wobble.")
        else:
            st.markdown('<div class="blinking">🔴 BEARING FAILURE</div>', unsafe_allow_html=True)
            st.error(f"**Critical:** High frequency peak at {peak_freq:.2f} Hz.")
            st.markdown("**🛠 Fix:** Grinding sound? Replace motor immediately.")
