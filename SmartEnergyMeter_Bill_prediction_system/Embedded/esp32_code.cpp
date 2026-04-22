#include <WiFi.h>
#include <HTTPClient.h>

// ==============================
// WIFI CONFIG
// ==============================
const char* ssid = "YOUR_WIFI_NAME";           // give some user name eg: sk510
const char* password = "YOUR_WIFI_PASSWORD";   // some password: 05102004

// Flask server IP (laptop hotspot / same network) ------------------------------
const char* serverURL = "http://192.168.1.10:5000/data";   // cmd- ipconfig -> ipv4 address put here dood...
//---------------------------------------------------------// instead of this  192.168.1.10 --................
// ==============================
// SENSOR PINS
// ==============================
#define CURRENT_SENSOR_PIN 35   // ACS712
#define VOLTAGE_SENSOR_PIN 34   // ZMPT101B

// ==============================
// CALIBRATION VARIABLES
// ==============================
float current_offset = 0;
float voltage_scale = 250.0;   // tune this (important)
float sensitivity = 0.100;     // ACS712 20A module approx

// ==============================
// FILTER VARIABLES
// ==============================
float filteredCurrent = 0;
float filteredVoltage = 0;

// ==============================
// WIFI SETUP
// ==============================
void setup() {
  Serial.begin(115200);

  pinMode(CURRENT_SENSOR_PIN, INPUT);
  pinMode(VOLTAGE_SENSOR_PIN, INPUT);

  Serial.println("Calibrating current sensor...");

  calibrateCurrentSensor();

  Serial.println("Connecting WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected ✔");
}

// ==============================
// CALIBRATE CURRENT SENSOR (ZERO OFFSET)
// ==============================
void calibrateCurrentSensor() {
  long sum = 0;

  for (int i = 0; i < 500; i++) {
    sum += analogRead(CURRENT_SENSOR_PIN);
    delay(2);
  }

  current_offset = sum / 500.0;

  Serial.print("Current Offset: ");
  Serial.println(current_offset);
}

// ==============================
// READ CURRENT (FILTERED)
// ==============================
float readCurrent() {
  int raw = analogRead(CURRENT_SENSOR_PIN);

  float voltage = (raw / 4095.0) * 3.3;
  float offsetVoltage = (current_offset / 4095.0) * 3.3;

  float current = (voltage - offsetVoltage) / sensitivity;

  if (current < 0) current = -current;

  // simple low-pass filter
  filteredCurrent = (0.8 * filteredCurrent) + (0.2 * current);

  return filteredCurrent;
}

// ==============================
// READ VOLTAGE (FILTERED)
// ==============================
float readVoltage() {
  int raw = analogRead(VOLTAGE_SENSOR_PIN);

  float voltage = (raw / 4095.0) * voltage_scale;

  filteredVoltage = (0.8 * filteredVoltage) + (0.2 * voltage);

  return filteredVoltage;
}

// ==============================
// MAIN LOOP
// ==============================
void loop() {

  float voltage = readVoltage();
  float current = readCurrent();

  float power = voltage * current;

  if (power < 0) power = 0;

  // fake hour removed → real system ready
  int hour_of_day = random(0, 24);

  // ==============================
  // JSON PACKET (FLASK READY)
  // ==============================
  String json = "{";
  json += "\"voltage\":" + String(voltage) + ",";
  json += "\"current\":" + String(current) + ",";
  json += "\"power\":" + String(power) + ",";
  json += "\"hour\":" + String(hour_of_day);
  json += "}";

  // ==============================
  // SEND TO FLASK
  // ==============================
  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    int response = http.POST(json);

    Serial.println("Sent: " + json);
    Serial.println("Response: " + String(response));

    http.end();
  } else {
    Serial.println("WiFi disconnected ❌");
  }

  delay(2000); // sampling time
}