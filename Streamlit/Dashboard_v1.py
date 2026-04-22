import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import plotly.graph_objects as go
from datetime import datetime

# ==============================
# LOAD MODEL + SCALER
# ==============================
model = joblib.load("energy_model.pkl")
scaler = joblib.load("scaler.pkl")

# ==============================
# INDIAN TARIFF FUNCTION
# ==============================
def calculate_bill(units):
    bill = 0

    if units <= 100:
        bill = units * 3.5
    elif units <= 200:
        bill = 100 * 3.5 + (units - 100) * 5.5
    elif units <= 300:
        bill = 100 * 3.5 + 100 * 5.5 + (units - 200) * 8
    else:
        bill = 100 * 3.5 + 100 * 5.5 + 100 * 8 + (units - 300) * 10

    return bill

# ==============================
# PAGE SETUP
# ==============================
st.set_page_config(page_title="Smart Energy Meter", layout="wide")
st.title("⚡ Smart Energy Meter (Mini Project)")

# ==============================
# SESSION STATE STORAGE
# ==============================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "power", "hour", "energy"])

if "last_power" not in st.session_state:
    st.session_state.last_power = 60

# ==============================
# INPUT MODE
# ==============================
st.sidebar.header("Input Source")

mode = st.sidebar.selectbox(
    "Choose Mode",
    ["ESP32 Simulation", "Manual Input"]
)

# ==============================
# INPUT DATA
# ==============================
if mode == "Manual Input":
    power = st.sidebar.slider("Power (W)", 0, 150, 60)
    hour = st.sidebar.slider("Hour of Day", 0, 23, datetime.now().hour)
else:
    power = st.sidebar.number_input("ESP32 Power (W)", value=st.session_state.last_power)
    hour = datetime.now().hour

# store last value
st.session_state.last_power = power

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

st.session_state.data = pd.concat(
    [st.session_state.data, new_data],
    ignore_index=True
)

# ==============================
# BILL CALCULATION
# ==============================
total_energy = st.session_state.data["energy"].sum()
bill = calculate_bill(total_energy * 1000)

# ==============================
# METRICS
# ==============================
col1, col2, col3 = st.columns(3)

col1.metric("⚡ Power (W)", f"{power}")
col2.metric("🔋 Energy (kWh)", f"{energy:.4f}")
col3.metric("💰 Bill (₹)", f"{bill:.2f}")

# ==============================
# GRAPH
# ==============================
st.subheader("📊 Live Energy Monitoring")

fig = go.Figure()

fig.add_trace(go.Scatter(
    y=st.session_state.data["power"],
    mode="lines+markers",
    name="Power (W)"
))

fig.add_trace(go.Scatter(
    y=st.session_state.data["energy"],
    mode="lines+markers",
    name="Energy (kWh)"
))

st.plotly_chart(fig, use_container_width=True)

# ==============================
# STATUS
# ==============================
st.subheader("🔌 System Status")

if mode == "ESP32 Simulation":
    st.success("🟢 ESP32 Mode Active (Simulation Ready for Hardware)")
else:
    st.info("🟡 Manual Mode Active")

# ==============================
# AUTO UPDATE
# ==============================
time.sleep(2)
st.rerun()