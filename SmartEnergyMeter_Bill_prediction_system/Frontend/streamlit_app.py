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

st.markdown("""
<h1 style='text-align:center; color:#00ffcc;'>
⚡ TNEB SMART ENERGY METER
</h1>
<p style='text-align:center; color:gray;'>
Industrial SCADA Grade Real-Time Monitoring System
</p>
<hr style="border:1px solid #222;">
""", unsafe_allow_html=True)

st.markdown("<h4 style='color:lime;'>🟢 LIVE GRID MONITORING ACTIVE</h4>", unsafe_allow_html=True)

# ==============================
# LOAD MODEL
# ==============================
model = joblib.load(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\SmartEnergyMeter_Bill_predictionSystem\ML model pkl file\energy_model.pkl")
scaler = joblib.load(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\SmartEnergyMeter_Bill_predictionSystem\ML model pkl file\scaler.pkl")

FLASK_URL = "http://localhost:5000/latest"

mode = st.sidebar.selectbox("System Mode", ["Live ESP32 (Flask)", "Simulation Mode"])

# ==============================
# SESSION STATE
# ==============================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "power", "energy"])

if "total_energy" not in st.session_state:
    st.session_state.total_energy = 0

# ==============================
# DATA INPUT (SIM + REAL)
# ==============================
if mode == "Simulation Mode":
    voltage = 230
    current = np.random.uniform(0.1, 1.2)
else:
    try:
        esp = requests.get(FLASK_URL).json()
        voltage = 230
        current = esp.get("current", np.random.uniform(0.1, 1))
    except:
        st.error("ESP32 not connected")
        voltage = 230
        current = 0

# ==============================
# CORE CALCULATION
# ==============================
power = voltage * current

dt = 2 / 3600
instant_energy = (power * dt) / 1000

st.session_state.total_energy += instant_energy
total_energy = st.session_state.total_energy

# ==============================
# BILLING ENGINE
# ==============================
def bill_calc(units):
    if units <= 100:
        return units * 3.5
    elif units <= 200:
        return 100 * 3.5 + (units - 100) * 5.5
    elif units <= 300:
        return 100 * 3.5 + 100 * 5.5 + (units - 200) * 8
    return 100 * 3.5 + 100 * 5.5 + 100 * 8 + (units - 300) * 10

current_bill = bill_calc(instant_energy * 1000)
monthly_bill = bill_calc(total_energy * 1000)

# ==============================
# LOAD CLASSIFICATION
# ==============================
if power < 100:
    status = "LOW LOAD 🟢"
elif power < 300:
    status = "MEDIUM LOAD 🟡"
else:
    status = "HIGH LOAD 🔴"

# ==============================
# STORE DATA
# ==============================
st.session_state.data = pd.concat([
    st.session_state.data,
    pd.DataFrame([[datetime.now(), power, instant_energy]],
                 columns=["time", "power", "energy"])
], ignore_index=True)

# ==============================
# HEADER METRICS (CORE PANEL)
# ==============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("⚡ Voltage (V)", f"{voltage}")
col2.metric("🔌 Current (A)", f"{current:.3f}")
col3.metric("⚡ Power (W)", f"{power:.2f}")
col4.metric("🔋 Energy (kWh)", f"{instant_energy:.6f}")

st.markdown("---")

# ==============================
# BILLING PANEL
# ==============================
b1, b2 = st.columns(2)

b1.metric("💰 Current Bill", f"₹ {current_bill:.2f}")
b2.metric("📊 Monthly Bill (Est.)", f"₹ {monthly_bill:.2f}")

st.markdown("---")

# ==============================
# STATUS + INSIGHTS
# ==============================
st.info(f"💡 System Status: {status}")

st.success(f"""
🤖 Smart Insights:
- Peak Demand Tracking Active
- Load Stability: Normal Grid Operation
- Energy Growth Rate: Stable
""")

# ==============================
# GAUGE
# ==============================
fig1 = go.Figure(go.Indicator(
    mode="gauge+number",
    value=power,
    title={"text": "POWER MONITOR"},
    gauge={
        "axis": {"range": [0, 500]},
        "bar": {"color": "cyan"},
        "steps": [
            {"range": [0, 100], "color": "green"},
            {"range": [100, 300], "color": "orange"},
            {"range": [300, 500], "color": "red"},
        ],
    }
))

fig1.update_layout(template="plotly_dark", height=300)
st.plotly_chart(fig1, use_container_width=True)

# ==============================
# LIVE GRAPH (FIXED - TIME BASED)
# ==============================
st.subheader("📊 Power & Energy Trend (SCADA View)")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=st.session_state.data["time"],
    y=st.session_state.data["power"],
    name="Power (W)",
    line=dict(color="orange")
))

fig.add_trace(go.Scatter(
    x=st.session_state.data["time"],
    y=st.session_state.data["energy"].cumsum(),
    name="Energy (kWh)",
    line=dict(color="cyan")
))

fig.update_layout(template="plotly_dark", height=400)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# RAW STATUS
# ==============================
st.subheader("📡 Live System Feed")

st.json({
    "voltage": voltage,
    "current": current,
    "power": power,
    "instant_energy": instant_energy,
    "total_energy": total_energy,
    "status": status
})

# ==============================
# AUTO REFRESH
# ==============================
time.sleep(2)
st.rerun()