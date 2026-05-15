#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SoftwareSerial.h>

// === CONFIGURATION ===
const char* SSID = "YOUR_SSID";
const char* PASSWORD = "YOUR_PASSWORD";
const char* SERVER_URL = "http://YOUR_PC_IP:8000/sensor";

const int WIFI_TIMEOUT = 20000;  // WiFi connection timeout (ms)
const int HTTP_TIMEOUT = 5000;   // HTTP request timeout (ms)
const int SENSOR_READ_INTERVAL = 5000;  // Read interval (ms)
const int RETRY_ATTEMPTS = 3;    // Number of retry attempts

// === VARIABLES ===
WiFiClient wifiClient;
int moistureValue = 0;
unsigned long lastReadTime = 0;

void setup() {
  // CRITICAL: Must match Arduino's baud rate (9600)
  Serial.begin(9600);
  delay(1000);
  
  Serial.println("\n[ESP8266] Starting initialization...");
  
  // Connect to WiFi
  connectToWiFi();
}

void connectToWiFi() {
  Serial.print("[WiFi] Connecting to ");
  Serial.println(SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);
  
  unsigned long startTime = millis();
  
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - startTime > WIFI_TIMEOUT) {
      Serial.println("[WiFi] Connection timeout - will retry in loop");
      return;
    }
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("[WiFi] Connected successfully");
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());
}

bool sendSensorData(int moisture) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] WiFi not connected - attempting reconnect");
    connectToWiFi();
    if (WiFi.status() != WL_CONNECTED) {
      return false;
    }
  }
  
  HTTPClient http;
  http.setTimeout(HTTP_TIMEOUT);
  
  if (!http.begin(wifiClient, SERVER_URL)) {
    Serial.println("[HTTP] Failed to begin HTTP");
    return false;
  }
  
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  String jsonPayload = "{\"moisture\":" + String(moisture) + "}";
  
  Serial.print("[HTTP] Sending: ");
  Serial.println(jsonPayload);
  
  int responseCode = http.POST(jsonPayload);
  
  if (responseCode == 200 || responseCode == 201) {
    Serial.println("[HTTP] SUCCESS " + String(responseCode));
    http.end();
    return true;
  } else if (responseCode > 0) {
    Serial.print("[HTTP] Error - Response code: ");
    Serial.println(responseCode);
    String response = http.getString();
    Serial.println(response);
  } else {
    Serial.print("[HTTP] Connection error: ");
    Serial.println(http.errorToString(responseCode));
  }
  
  http.end();
  return false;
}

void readAndSendSensorData() {
  // Read from Arduino via Serial
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    // Parse CSV format: "moisture,pumpStatus"
    int commaIndex = data.indexOf(',');
    if (commaIndex > 0) {
      String moistureStr = data.substring(0, commaIndex);
      String pumpStatusStr = data.substring(commaIndex + 1);
      
      moistureValue = moistureStr.toInt();
      int pumpStatus = pumpStatusStr.toInt();
      
      Serial.print("[Sensor] Read moisture: ");
      Serial.print(moistureValue);
      Serial.print(", Pump: ");
      Serial.println(pumpStatus ? "ON" : "OFF");
      
      // Attempt to send with retry logic
      int attempts = 0;
      while (attempts < RETRY_ATTEMPTS) {
        if (sendSensorData(moistureValue)) {
          break;
        }
        attempts++;
        if (attempts < RETRY_ATTEMPTS) {
          Serial.print("[HTTP] Retry attempt ");
          Serial.print(attempts);
          Serial.println("...");
          delay(1000);
        }
      }
    }
  }
}

void loop() {
  // Read and send sensor data continuously
  readAndSendSensorData();
  
  // Periodic WiFi health check
  static unsigned long lastWiFiCheck = 0;
  if (millis() - lastWiFiCheck > 30000) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("[WiFi] Disconnected - reconnecting...");
      connectToWiFi();
    }
    lastWiFiCheck = millis();
  }
  
  delay(100);  // Small delay to prevent watchdog issues
}