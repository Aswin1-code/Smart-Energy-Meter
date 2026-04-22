import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================
# PAGE
# ==============================
st.set_page_config(page_title="TNEB Smart Meter", layout="wide")

st.markdown("""
<h1 style='text-align:center; color:#00ffcc;'>
⚡ TNEB SMART ENERGY BILLING SYSTEM
</h1>
<p style='text-align:center; color:gray;'>
Real Billing Cycle + Peak Demand + SCADA Analytics
</p>
<hr>
""", unsafe_allow_html=True)

FLASK_URL = "http://localhost:5000/latest"

mode = st.sidebar.selectbox("Mode", ["Live ESP32", "Simulation"])

# ==============================
# SESSION INIT
# ==============================
if "records" not in st.session_state:
    st.session_state.records = []

if "daily_energy" not in st.session_state:
    st.session_state.daily_energy = 0

if "monthly_energy" not in st.session_state:
    st.session_state.monthly_energy = 0

if "peak_power" not in st.session_state:
    st.session_state.peak_power = 0

if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.now().date()

# ==============================
# SLAB BILLING (TNEB STYLE)
# ==============================
def bill(units):
    if units <= 100:
        return units * 3.5
    elif units <= 200:
        return 100*3.5 + (units-100)*5.5
    elif units <= 300:
        return 100*3.5 + 100*5.5 + (units-200)*8
    else:
        return 100*3.5 + 100*5.5 + 100*8 + (units-300)*10

# ==============================
# DATA INPUT
# ==============================
if mode == "Simulation":
    power = np.random.randint(40, 180)
    hour = datetime.now().hour
else:
    try:
        data = requests.get(FLASK_URL).json()
        power = data["power"]
        hour = data["hour"]
    except:
        power = 0
        hour = datetime.now().hour

# ==============================
# DAILY RESET LOGIC
# ==============================
today = datetime.now().date()

if today != st.session_state.last_reset:
    st.session_state.daily_energy = 0
    st.session_state.last_reset = today

# ==============================
# ENERGY CALCULATION
# ==============================
dt = 2 / 3600
instant_energy = (power * dt) / 1000

st.session_state.daily_energy += instant_energy
st.session_state.monthly_energy += instant_energy

# ==============================
# PEAK DEMAND
# ==============================
if power > st.session_state.peak_power:
    st.session_state.peak_power = power

# ==============================
# STORE DATA
# ==============================
st.session_state.records.append({
    "time": datetime.now(),
    "power": power,
    "energy": instant_energy,
    "daily": st.session_state.daily_energy,
    "monthly": st.session_state.monthly_energy
})

df = pd.DataFrame(st.session_state.records)

# ==============================
# BILLING
# ==============================
daily_bill = bill(st.session_state.daily_energy * 1000)
monthly_bill = bill(st.session_state.monthly_energy * 1000)

# ==============================
# DASHBOARD
# ==============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("⚡ Power", f"{power} W")
col2.metric("📊 Daily Energy", f"{st.session_state.daily_energy:.4f} kWh")
col3.metric("📅 Monthly Bill", f"₹ {monthly_bill:.2f}")
col4.metric("🔥 Peak Demand", f"{st.session_state.peak_power} W")

st.markdown("---")

# ==============================
# BILL HISTORY GRAPH
# ==============================
st.subheader("📊 Bill History Trend")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["time"],
    y=df["daily"],
    name="Daily Energy",
    line=dict(color="cyan")
))

fig.add_trace(go.Scatter(
    x=df["time"],
    y=df["monthly"],
    name="Monthly Energy",
    line=dict(color="orange")
))

fig.update_layout(template="plotly_dark", height=400)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# RAW
# ==============================
st.json({
    "daily_energy": st.session_state.daily_energy,
    "monthly_energy": st.session_state.monthly_energy,
    "peak_power": st.session_state.peak_power
})

time.sleep(2)
st.rerun()