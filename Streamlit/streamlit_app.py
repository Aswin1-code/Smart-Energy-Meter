import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import requests
import plotly.graph_objects as go
from datetime import datetime
import os

# ==============================
# PAGE SETUP
# ==============================
st.set_page_config(page_title="TNEB Smart Meter", layout="wide")

# ==============================
# HEADER (SCADA STYLE)
# ==============================
st.markdown("""
<h1 style='text-align:center; color:#00ffcc;'>
⚡ TNEB SMART ENERGY METER
</h1>
<p style='text-align:center; color:gray;'>
Industrial SCADA Grade Real-Time Monitoring System (IoT + ML)
</p>
<hr style="border:1px solid #222;">
""", unsafe_allow_html=True)

st.markdown("<h4 style='color:lime;'>🟢 LIVE GRID MONITORING ACTIVE</h4>", unsafe_allow_html=True)

# ==============================
# LOAD MODEL
# ==============================
model = joblib.load(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\ML model pkl file\energy_model.pkl")
scaler = joblib.load(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\ML model pkl file\scaler.pkl")

FLASK_URL = "http://localhost:5000/latest"

# ==============================
# MODE SELECTION
# ==============================
mode = st.sidebar.selectbox("System Mode", ["Live ESP32 (Flask)", "Simulation Mode"])

# ==============================
# TARIFF
# ==============================
def calculate_bill(units):
    if units <= 100:
        return units * 3.5
    elif units <= 200:
        return 100 * 3.5 + (units - 100) * 5.5
    elif units <= 300:
        return 100 * 3.5 + 100 * 5.5 + (units - 200) * 8
    else:
        return 100 * 3.5 + 100 * 5.5 + 100 * 8 + (units - 300) * 10

# ==============================
# SESSION DATA
# ==============================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "power", "hour", "energy"])

# ==============================
# DATA SOURCE (SYNC SIM + REAL)
# ==============================
if mode == "Simulation Mode":
    power = np.random.randint(50, 180)
    hour = datetime.now().hour
    esp_data = {"power": power, "hour": hour}
else:
    try:
        response = requests.get(FLASK_URL)
        esp_data = response.json()
        power = esp_data["power"]
        hour = esp_data["hour"]
    except:
        st.error("❌ ESP32 / Flask not connected")
        power = 0
        hour = datetime.now().hour
        esp_data = {"power": power, "hour": hour}

# ==============================
# ML PREDICTION
# ==============================
input_data = np.array([[power, hour]])
energy = model.predict(scaler.transform(input_data))[0]

# ==============================
# STORE DATA
# ==============================
new_data = pd.DataFrame([[datetime.now(), power, hour, energy]],
                        columns=["time", "power", "hour", "energy"])

st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

# ==============================
# CSV LOGGING
# ==============================
file_path = "energy_log.csv"

if not os.path.exists(file_path):
    new_data.to_csv(file_path, index=False)
else:
    new_data.to_csv(file_path, mode="a", header=False, index=False)

# ==============================
# TOTAL METRICS (FIXED LOGIC)
# ==============================
total_energy = st.session_state.data["energy"].sum()

current_bill = calculate_bill(energy * 1000)
total_bill = calculate_bill(total_energy * 1000)

# ==============================
# SMART DASHBOARD UI (TNEB STYLE)
# ==============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("⚡ Power (W)", f"{power:.2f}")
col2.metric("🔋 Instant Energy (kWh)", f"{energy:.4f}")
col3.metric("💰 Current Bill", f"₹ {current_bill:.2f}")
col4.metric("📊 Total Bill", f"₹ {total_bill:.2f}")

st.markdown("---")

# ==============================
# ⚡ ANALOG POWER GAUGE (SMART METER DIAL)
# ==============================
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=power,
    title={'text': "POWER METER (W)"},
    gauge={
        'axis': {'range': [0, 200]},
        'bar': {'color': "cyan"},
        'steps': [
            {'range': [0, 80], 'color': "green"},
            {'range': [80, 150], 'color': "orange"},
            {'range': [150, 200], 'color': "red"},
        ],
    }
))

gauge.update_layout(template="plotly_dark", height=300)
st.plotly_chart(gauge, use_container_width=True)

# ==============================
# 📈 LIVE LOAD WAVEFORM (OSCILLOSCOPE STYLE)
# ==============================
st.subheader("📈 Load Waveform (Grid Behavior)")

fig = go.Figure()

fig.add_trace(go.Scatter(
    y=st.session_state.data["power"],
    mode="lines",
    name="Load Profile",
    line=dict(color="lime", width=2)
))

fig.add_trace(go.Scatter(
    y=st.session_state.data["energy"],
    mode="lines",
    name="Energy Profile",
    line=dict(color="cyan", width=2)
))

fig.update_layout(
    template="plotly_dark",
    height=380,
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# RAW DATA
# ==============================
st.subheader("📡 Live ESP32 Feed")
st.json(esp_data)

# ==============================
# AUTO REFRESH
# ==============================
time.sleep(2)
st.rerun()