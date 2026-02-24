import streamlit as st
import pandas as pd
import numpy as np

# Configure the page layout to be wide
st.set_page_config(page_title="Drone Vibration Diagnostics", layout="wide")
st.title("🚁 Drone Vibration & Failure Analysis")

# Divide the screen into a 2x2 grid (4 sections)
top_left, top_right = st.columns(2)
bottom_left, bottom_right = st.columns(2)

# ==========================================
# SECTION 1: Data Input & Raw Display
# ==========================================
with top_left:
    st.header("1. Data Input")
    uploaded_file = st.file_uploader("Upload your VIBRATE.CSV from the SD Card", type=["csv"])

if uploaded_file is not None:
    # Read the CSV. The Arduino outputs two columns: Raw, G-Force
    df = pd.read_csv(uploaded_file, header=None, names=["Raw", "G_Force"])
    
    with top_left:
        st.write("Raw Vibration Waveform (Amplitude vs Time)")
        st.line_chart(df["G_Force"])

    # ==========================================
    # SECTION 2: FFT Calculation & Graph
    # ==========================================
    with top_right:
        st.header("2. Frequency Spectrum (FFT)")
        
        # FFT Math variables
        N = len(df)       # Number of readings (e.g., 1024)
        T = 0.01          # Sample spacing (10ms from your Arduino code)
        
        # Calculate FFT using numpy
        yf = np.fft.fft(df["G_Force"])
        xf = np.fft.fftfreq(N, T)[:N//2]
        magnitude = 2.0/N * np.abs(yf[0:N//2])
        magnitude[0] = 0  # Remove the DC offset (0 Hz) so it doesn't skew the graph
        
        # Plot the FFT
        fft_data = pd.DataFrame({"Frequency (Hz)": xf, "Magnitude (G)": magnitude}).set_index("Frequency (Hz)")
        st.line_chart(fft_data)
        
        # Find the peak frequency for the diagnostics
        peak_freq = xf[np.argmax(magnitude)]
        peak_mag = np.max(magnitude)

    # ==========================================
    # SECTION 3: Assumption Indicator Table
    # ==========================================
    with bottom_left:
        st.header("3. Failure Reference Guide")
        st.markdown("""
        | Frequency Range | Assumed Condition / Failure |
        | :--- | :--- |
        | **0 Hz - 5 Hz** | Normal / Safe Operation |
        | **10 Hz - 30 Hz** | Unbalanced Propeller |
        | **50 Hz - 80 Hz** | Bent Motor Shaft |
        | **100+ Hz** | Bad Motor Bearing / High-Frequency Resonance |
        """)

    # ==========================================
    # SECTION 4: Auto-Diagnostic Output
    # ==========================================
    with bottom_right:
        st.header("4. System Status")
        
        # Display the exact peak found
        st.metric(label="Peak Frequency Detected", value=f"{peak_freq:.2f} Hz", delta=f"{peak_mag:.2f} Gs")
        
        # Logic to determine the failure type
        if peak_mag < 0.2: 
            st.success("✅ **STATUS: NORMAL.** Vibration levels are minimal and safe.")
        elif 10 <= peak_freq <= 30:
            st.error("🚨 **WARNING: Unbalanced Propeller detected!** Check blades for chips or debris.")
        elif 50 <= peak_freq <= 80:
            st.error("🚨 **WARNING: Bent Motor Shaft detected!** Inspect motor bells and shafts.")
        elif peak_freq >= 100:
            st.error("🚨 **WARNING: Bad Motor Bearing detected!** High-frequency grinding detected.")
        else:
            st.warning("⚠️ **NOTICE:** Anomalous vibration detected outside standard profiles.")

else:
    # Message shown when no file is uploaded yet
    st.info("Please upload your CSV file to begin the automatic FFT analysis.")
