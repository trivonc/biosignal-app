import numpy as np
import pandas as pd

fs = 1000  # 1000 Hz sampling rate
t = np.linspace(0, 5, 5 * fs)  # 5 seconds

# 1. Generate Synthetic ECG
ecg = (
    0.5 * np.sin(2 * np.pi * 1.2 * t)
    + 1.8 * np.sin(2 * np.pi * 1.2 * t) ** 10
    + 0.15 * np.random.normal(0, 1, len(t))
)
pd.DataFrame({"Time (s)": t, "ECG Lead I (mV)": ecg}).to_csv(
    "sample_ecg.csv", index=False
)

# 2. Generate Synthetic EMG (Burst activity)
emg_bursts = np.sin(2 * np.pi * 0.5 * t) ** 2
emg_noise = np.random.normal(0, 0.5, len(t))
emg = emg_bursts * emg_noise
pd.DataFrame({"Time (s)": t, "EMG Biceps (mV)": emg}).to_csv(
    "sample_emg.csv", index=False
)

print("Created sample_ecg.csv and sample_emg.csv!")
