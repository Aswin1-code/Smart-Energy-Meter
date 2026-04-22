from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_data = {
    "power": 0,
    "hour": 0,
    "time": str(datetime.now())
}

@app.route("/data", methods=["POST"])
def receive_data():
    global latest_data

    data = request.get_json()

    latest_data = {
        "power": float(data.get("power", 0)),
        "hour": int(data.get("hour", 0)),
        "time": str(datetime.now())
    }

    return jsonify({"status": "ok"})

@app.route("/latest")
def latest():
    return jsonify(latest_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)