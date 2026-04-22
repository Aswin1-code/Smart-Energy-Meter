import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import requests
import plotly.graph_objects as go
from datetime import datetime
import os   # ✅ ADDED

# ==============================
# PAGE SETUP (ONLY ONCE - FIXED)
# ==============================
st.set_page_config(page_title="Smart Energy Meter", layout="wide")

# ==============================
# SMART METER UI HEADER
# ==============================
st.markdown(
    """
    <h1 style='text-align:center; color:#00ffcc;'>
    ⚡ SMART ENERGY METER DASHBOARD
    </h1>
    <p style='text-align:center; color:gray;'>
    Real-time Energy Monitoring System (IoT + ML)
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

st.markdown("<h4 style='color:lime;'>🟢 LIVE SYSTEM ACTIVE</h4>", unsafe_allow_html=True)

# ==============================
# LOAD MODEL + SCALER
# ==============================
model = joblib.load(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\ML model pkl file\energy_model.pkl")
scaler = joblib.load(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\ML model pkl file\scaler.pkl")

# ==============================
# FLASK BACKEND URL
# ==============================
FLASK_URL = "http://localhost:5000/latest"

# ==============================
# TARIFF FUNCTION
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
# SESSION STORAGE
# ==============================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "power", "hour", "energy"])

# ==============================
# FETCH DATA FROM FLASK
# ==============================
try:
    response = requests.get(FLASK_URL)
    esp_data = response.json()

    power = esp_data["power"]
    hour = esp_data["hour"]

except:
    st.error("❌ ESP32/Flask not connected")
    power = 0
    hour = datetime.now().hour
    esp_data = {"power": 0, "hour": hour}

# ==============================
# ML PREDICTION
# ==============================
input_data = np.array([[power, hour]])
scaled_input = scaler.transform(input_data)
energy = model.predict(scaled_input)[0]

# ==============================
# STORE DATA
# ==============================
new_data = pd.DataFrame(
    [[datetime.now(), power, hour, energy]],
    columns=["time", "power", "hour", "energy"]
)

st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

# ==============================
# 🚗 CSV LOGGING (ADDED PART)
# ==============================
file_path = "energy_log.csv"

if not os.path.exists(file_path):
    new_data.to_csv(file_path, index=False)
else:
    new_data.to_csv(file_path, mode="a", header=False, index=False)

# ==============================
# BILL CALCULATION
# ==============================
total_energy = st.session_state.data["energy"].sum()
bill = calculate_bill(total_energy * 1000)

# ==============================
# SMART METER CARDS UI
# ==============================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div style="padding:20px;border-radius:15px;background-color:#111827;text-align:center;">
        <h3 style="color:#00ffcc;">⚡ POWER</h3>
        <h2 style="color:white;">{power:.2f} W</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="padding:20px;border-radius:15px;background-color:#111827;text-align:center;">
        <h3 style="color:#00ffcc;">🔋 ENERGY</h3>
        <h2 style="color:white;">{energy:.4f} kWh</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="padding:20px;border-radius:15px;background-color:#111827;text-align:center;">
        <h3 style="color:#00ffcc;">💰 BILL</h3>
        <h2 style="color:white;">₹ {bill:.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================
# GRAPH
# ==============================
st.subheader("📊 Energy Consumption Trend")

fig = go.Figure()

fig.add_trace(go.Scatter(
    y=st.session_state.data["power"],
    mode="lines",
    name="Power (W)",
    line=dict(color="orange", width=3)
))

fig.add_trace(go.Scatter(
    y=st.session_state.data["energy"],
    mode="lines",
    name="Energy (kWh)",
    line=dict(color="cyan", width=3)
))

fig.update_layout(
    template="plotly_dark",
    height=400,
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# RAW DATA
# ==============================
st.subheader("📡 Live ESP32 Data")
st.json(esp_data)

# ==============================
# AUTO REFRESH
# ==============================
time.sleep(2)
st.rerun()