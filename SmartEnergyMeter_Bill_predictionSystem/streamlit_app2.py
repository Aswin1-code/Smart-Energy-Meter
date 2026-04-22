import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import requests
import plotly.graph_objects as go
from datetime import datetime

# ==============================
# PAGE SETUP
# ==============================
st.set_page_config(page_title="TNEB Smart Meter", layout="wide")

st.markdown("""
<h1 style='text-align:center; color:#00ffcc;'>
⚡ TNEB SMART ENERGY METER
</h1>
<p style='text-align:center; color:gray;'>
Real IoT + Energy Analytics System (SCADA Mode)
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

mode = st.sidebar.selectbox("System Mode", ["Live ESP32 (Flask)", "Simulation Mode"])

# ==============================
# BILL FUNCTION
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
# SESSION STATE
# ==============================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "power", "energy"])

if "total_energy" not in st.session_state:
    st.session_state.total_energy = 0

# ==============================
# DATA SOURCE (SIM + ESP32 SAME FORMAT)
# ==============================
if mode == "Simulation Mode":
    power = np.random.randint(40, 180)
    hour = datetime.now().hour
else:
    try:
        esp = requests.get(FLASK_URL).json()
        power = esp["power"]
        hour = esp["hour"]
    except:
        st.error("ESP32 not connected")
        power = 0
        hour = datetime.now().hour

# ==============================
# ENERGY MODEL (REAL PHYSICS CORRECT)
# ==============================
dt = 2 / 3600  # 2 sec sampling

instant_energy = (power * dt) / 1000  # kWh increment

st.session_state.total_energy += instant_energy
total_energy = st.session_state.total_energy

# ==============================
# BILLING (CORRECT)
# ==============================
current_bill = calculate_bill(total_energy * 1000)
total_bill = calculate_bill(total_energy * 1000)

# ==============================
# STORE DATA
# ==============================
new_row = pd.DataFrame([[datetime.now(), power, instant_energy]],
                       columns=["time", "power", "energy"])

st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)

# ==============================
# DASHBOARD
# ==============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("⚡ Power (W)", f"{power:.2f}")
col2.metric("🔋 Instant Energy (kWh)", f"{instant_energy:.6f}")
col3.metric("📊 Total Energy (kWh)", f"{total_energy:.4f}")
col4.metric("💰 Total Bill (₹)", f"{total_bill:.2f}")

st.markdown("---")

# ==============================
# POWER GAUGE
# ==============================
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=power,
    title={'text': "POWER METER"},
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
# SCADA STYLE GRAPH (FIXED LOGIC)
# ==============================
st.subheader("📈 SCADA Energy Monitoring (Correct Physics Model)")

fig = go.Figure()

# Power vs Time
fig.add_trace(go.Scatter(
    x=st.session_state.data["time"],
    y=st.session_state.data["power"],
    mode="lines",
    name="Power (W)",
    line=dict(color="orange")
))

# True cumulative energy
fig.add_trace(go.Scatter(
    x=st.session_state.data["time"],
    y=st.session_state.data["energy"].cumsum(),
    mode="lines",
    name="Energy (kWh)",
    line=dict(color="cyan")
))

fig.update_layout(
    template="plotly_dark",
    height=400,
    xaxis_title="Time",
    yaxis_title="Value"
)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# RAW DATA
# ==============================
st.json({
    "power": power,
    "instant_energy": instant_energy,
    "total_energy": total_energy,
    "bill": total_bill
})

# ==============================
# REFRESH
# ==============================
time.sleep(2)
st.rerun()