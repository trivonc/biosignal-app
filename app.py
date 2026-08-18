import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Biomedical Signal Visualiser")
st.write("Upload a ECG/EMG CSV file to plot physiological data.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head())
    
    # Select column to plot
    selected_col = st.selectbox("Select signal channel:", df.columns)
    
    # Interactive plot
    fig = px.line(df, y=selected_col, title=f"Waveform: {selected_col}")
    st.plotly_chart(fig)
