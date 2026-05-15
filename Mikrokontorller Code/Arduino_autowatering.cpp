// === PIN CONFIGURATION ===
#define SENSOR_PIN A0      // Soil moisture sensor analog input
#define RELAY_PIN 8        // Relay module digital control pin
#define SENSOR_READINGS 5  // Number of readings for averaging

// === CONFIGURATION ===
int dryThreshold = 600;       // Higher value = drier soil (adjust 400-800 based on calibration)
int readingDelay = 2000;      // Delay between sensor reads (ms)
int pumpOffTime = 3000;       // Minimum pump ON duration (ms)

// === VARIABLES ===
int moistureValue = 0;
int averageValue = 0;
unsigned long pumpStartTime = 0;
bool isPumpOn = false;

void setup() {
  Serial.begin(9600);  // CRITICAL: Match ESP8266 serial config - do NOT change
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);  // Relay OFF (high = inactive for typical relay modules)
  delay(500);
  Serial.println("[Arduino] Initialization complete");
}

void loop() {
  // === READ SENSOR WITH AVERAGING ===
  long sensorSum = 0;
  for (int i = 0; i < SENSOR_READINGS; i++) {
    sensorSum += analogRead(SENSOR_PIN);
    delay(50);
  }
  averageValue = sensorSum / SENSOR_READINGS;

  // === AUTO WATERING LOGIC ===
  // NOTE: analogRead returns 0-1023; higher value = DRIER soil
  if (averageValue > dryThreshold && !isPumpOn) {
    // SOIL IS DRY → ACTIVATE PUMP
    digitalWrite(RELAY_PIN, LOW);
    isPumpOn = true;
    pumpStartTime = millis();
    Serial.println("PUMP ON");
  } 
  else if ((millis() - pumpStartTime) > pumpOffTime && isPumpOn && averageValue < (dryThreshold - 50)) {
    // SOIL IS WET + minimum pump time reached → DEACTIVATE PUMP
    digitalWrite(RELAY_PIN, HIGH);
    isPumpOn = false;
    Serial.println("PUMP OFF");
  }

  // === SEND DATA TO ESP8266 (Single transmission) ===
  Serial.print(averageValue);
  Serial.println("," + String(isPumpOn ? 1 : 0));

  delay(readingDelay);
}