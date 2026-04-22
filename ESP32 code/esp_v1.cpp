#include <WiFi.h>
#include <HTTPClient.h>

// ==============================
// WiFi Credentials
// ==============================
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ==============================
// Streamlit Server IP
// (replace with your laptop IP)
// ==============================
const char* serverURL = "http://192.168.1.10:8501/data";

void setup() {
  Serial.begin(115200);

  // Connect WiFi
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi ✔");
}

void loop() {

  // ==============================
  // SIMULATED SENSOR VALUES
  // (Replace later with ACS712 + ZMPT101B)
  // ==============================

  float voltage = 230.0;

  // simulate current (0.5A to 3A)
  float current = random(50, 300) / 100.0;

  float power = voltage * current;

  // get hour of day (simple simulation)
  int hour_of_day = random(0, 24);

  // ==============================
  // JSON FORMAT
  // ==============================
  String json = "{";
  json += "\"power\":" + String(power) + ",";
  json += "\"hour\":" + String(hour_of_day);
  json += "}";

  // ==============================
  // SEND DATA TO STREAMLIT
  // ==============================
  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    int responseCode = http.POST(json);

    Serial.print("Sent JSON: ");
    Serial.println(json);
    Serial.print("Response: ");
    Serial.println(responseCode);

    http.end();

  } else {
    Serial.println("WiFi Disconnected ❌");
  }

  delay(3000); // send every 3 seconds
}