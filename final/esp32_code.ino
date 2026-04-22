#include <WiFi.h>
#include <HTTPClient.h>

// ==============================
// WiFi Credentials
// ==============================

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ==============================
// FLASK SERVER (IMPORTANT FIX)
// ==============================
// Replace with your laptop IP running Flask

const char* serverURL = "http://192.168.1.10:5000/data";

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
  // REALISTIC LOAD SIMULATION (2 BULBS)
  // ==============================

  float voltage = 230.0;

  // simulate current for 2 bulbs (0 to 0.52A approx total)
  float bulb1 = (random(0, 2) ? 0.26 : 0.0);  // 60W bulb
  float bulb2 = (random(0, 2) ? 0.26 : 0.0);  // 60W bulb

  float current = bulb1 + bulb2;

  float power = voltage * current;

  // add small noise (real sensor behavior)
  power = power + random(-5, 5);

  if (power < 0) power = 0;

  // ==============================
  // USE REAL TIME INSTEAD OF RANDOM HOUR
  // ==============================
  int hour_of_day = random(0, 24);

  // ==============================
  // JSON FORMAT
  // ==============================
  String json = "{";
  json += "\"power\":" + String(power) + ",";
  json += "\"hour\":" + String(hour_of_day);
  json += "}";

  // ==============================
  // SEND TO FLASK BACKEND
  // ==============================
  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    int responseCode = http.POST(json);

    Serial.print("Sent JSON: ");
    Serial.println(json);
    Serial.print("Response Code: ");
    Serial.println(responseCode);

    http.end();

  } else {
    Serial.println("WiFi Disconnected ❌");
  }

  delay(2000); // send every 3 sec
}