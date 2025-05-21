

const int ecgPin = 34;  // Connect AD8232 OUT to A0 (or any analog pin)

void setup() {
  Serial.begin(115200);   // Start serial communication
}

void loop() {
  int ecgValue = analogRead(ecgPin);  // Read ECG signal (0–1023)
  Serial.println(ecgValue);           // Print value to Serial Plotter
  delay(4);                           // ~250 samples per second (1000 ms / 250)
}

