from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS   # ✅ ADDED

app = Flask(__name__)
CORS(app)  # ✅ ADDED (allows Streamlit/browser access)

# ==============================
# GLOBAL STORAGE (LATEST DATA)
# ==============================
latest_data = {
    "power": 0,
    "hour": 0,
    "time": str(datetime.now())
}

# ==============================
# STORE ESP32 DATA
# ==============================
@app.route("/data", methods=["POST"])
def receive_data():
    global latest_data

    data = request.get_json()  # ✅ safer than request.json

    if not data:
        return jsonify({"status": "failed", "reason": "no data"}), 400

    latest_data = {
        "power": data.get("power", 0),
        "hour": data.get("hour", 0),
        "time": str(datetime.now())
    }

    print("📡 Received from ESP32:", latest_data)

    return jsonify({"status": "success"}), 200


# ==============================
# SEND LATEST DATA TO STREAMLIT
# ==============================
@app.route("/latest", methods=["GET"])
def send_latest():
    return jsonify(latest_data)


# ==============================
# HEALTH CHECK
# ==============================
@app.route("/")
def home():
    return "🚗 Smart Energy Meter Flask Server Running"


# ==============================
# RUN SERVER
# ==============================
if __name__ == "__main__":
    print("🚀 Flask Server Starting...")
    app.run(host="0.0.0.0", port=5000, debug=True)