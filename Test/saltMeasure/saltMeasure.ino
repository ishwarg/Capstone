void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  // pinMode(7, OUTPUT);
  // analogWrite(7,240);
  // pinMode(10, OUTPUT);
  // analogWrite(10,240);
}

// the loop routine runs over and over again forever:
void loop() {
  // read the input on analog pin 0:
  
  Serial.println(analogRead(2));
  delay(1);  // delay in between reads for stability
}