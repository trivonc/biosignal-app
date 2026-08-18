import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.signal import find_peaks, butter, filtfilt

st.set_page_config(page_title="BME Signal Visualiser", layout="wide")

st.title("⚡ Biomedical Signal Visualiser & Analyzer")
st.write("Analyze ECG/EMG recordings, calculate peak statistics, and filter signal noise.")

# Sidebar controls
st.sidebar.header("Data Source & Controls")
data_source = st.sidebar.radio("Data Input Mode:", ["Use Sample Synthetic ECG", "Upload CSV File"])

sampling_rate = st.sidebar.number_input("Sampling Rate (Hz):", min_value=100, max_value=5000, value=1000)

df = None

if data_source == "Use Sample Synthetic ECG":
    st.sidebar.info("Synthetic ECG running at 1000 Hz.")
    t = np.linspace(0, 10, 10 * sampling_rate)
    
    # Synthetic ECG equation with high-frequency noise
    clean_ecg = 0.5 * np.sin(2 * np.pi * 1.2 * t) + 1.8 * np.sin(2 * np.pi * 1.2 * t)**10
    noise = 0.25 * np.random.normal(0, 1, len(t))
    
    df = pd.DataFrame({
        "Time (s)": t,
        "Raw ECG (mV)": clean_ecg + noise
    })
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

if df is not None:
    st.markdown("---")
    
    # Channel selection
    time_col = "Time (s)" if "Time (s)" in df.columns else None
    signal_cols = [col for col in df.columns if col != time_col]
    selected_col = st.sidebar.selectbox("Select Signal Channel:", signal_cols)
    
    raw_signal = df[selected_col].values
    
    # Noise Filtering Controls
    st.sidebar.markdown("---")
    st.sidebar.header("Noise Filtering")
    apply_filter = st.sidebar.checkbox("Apply Low-Pass Filter", value=True)
    cutoff_freq = st.sidebar.slider("Cutoff Frequency (Hz):", 1, 100, 35)
    
    # Peak Detection Controls
    st.sidebar.markdown("---")
    st.sidebar.header("Peak Detection Settings")
    detect_peaks = st.sidebar.checkbox("Detect Peaks", value=True)
    peak_threshold = st.sidebar.slider("Min Peak Amplitude:", 0.1, 3.0, 1.0)
    
    # Apply Butterworth Filter
    if apply_filter:
        nyquist = 0.5 * sampling_rate
        normal_cutoff = cutoff_freq / nyquist
        b, a = butter(2, normal_cutoff, btype='low', analog=False)
        active_signal = filtfilt(b, a, raw_signal)
        df["Filtered Signal"] = active_signal
        active_col = "Filtered Signal"
    else:
        active_signal = raw_signal
        active_col = selected_col
    
    # Statistical Calculations
    max_val = np.max(active_signal)
    min_val = np.min(active_signal)
    
    # Peak Detection & Metrics
    peaks, _ = find_peaks(active_signal, distance=int(sampling_rate * 0.4), height=peak_threshold)
    
    if len(peaks) > 1:
        # Calculate time intervals between consecutive peaks
        if time_col:
            peak_times = df[time_col].iloc[peaks].values
            intervals = np.diff(peak_times)
            avg_interval = np.mean(intervals)
        else:
            intervals_samples = np.diff(peaks)
            avg_interval = np.mean(intervals_samples) / sampling_rate
            
        bpm = 60.0 / avg_interval
    else:
        avg_interval = 0.0
        bpm = 0.0
        
    # Display BME Metrics Cards
    st.subheader("📊 Signal Metrics Overview")
    m1, m2, m3, m4, m5 = st.columns(5)
    
    m1.metric("Highest Recording", f"{max_val:.2f} mV")
    m2.metric("Lowest Recording", f"{min_val:.2f} mV")
    m3.metric("Heart Rate", f"{int(bpm)} BPM" if bpm > 0 else "N/A")
    m4.metric("Avg Peak Interval", f"{avg_interval:.3f} s" if avg_interval > 0 else "N/A")
    m5.metric("Total Peaks", len(peaks))

    # Plot Interactive Chart
    st.subheader("📈 Signal Waveform Plot")
    x_axis = df[time_col] if time_col else df.index
    
    fig = px.line(df, x=x_axis, y=active_col, title=f"Visualizing: {active_col}")
    
    if detect_peaks and len(peaks) > 0:
        fig.add_scatter(
            x=x_axis.iloc[peaks], 
            y=active_signal[peaks], 
            mode='markers', 
            name='Detected Peaks', 
            marker=dict(color='red', size=8, symbol='x')
        )
    
    fig.update_traces(line=dict(color="#00CC96", width=1.2))
    fig.update_layout(template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔍 View Raw Data Table"):
        st.dataframe(df)