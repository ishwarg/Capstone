#include <PID_v1.h>

#define WATERS 4
#define SALTS 2
#define WATERK 10
#define SALTK 7
#define CONCENTRATION_INLET 0
#define CONCENTRATION_OUTLET 0

#define RUN 1
#define CALIBRATE 2
#define FLUSH 3
#define CURVELOAD 4
#define STOP 5
#define SALT_MEASURE 9

#define CALIBRATION_TIME 10000
#define FLUSH_TIME 10000
#define MAX_ROWS 300
#define RAMP_TIME 20000

#define FULL_SPEED 255
#define OFF 0
#define WATER_SPEED 190
#define SALT_SPEED 120
#define WATER_MIN 85
#define SALT_MIN 80

#define SETPOINT_THRESHOLD 40
#define WINDOW_SIZE 100

#define SALTKP 0.1
#define SALTKI 0.0
#define SALTKD 0.00
#define WATERKP 0.0
#define WATERKI 0.0
#define WATERKD 0.0

#define UPPER_SETPOINT 180
#define LOWER_SETPOINT 40

double Setpoints, Inputs, Outputs;
double Setpointk, Inputk, Outputk;


double Kps = SALTKP, Kis = SALTKI, Kds = SALTKD;
PID myPIDS(&Inputs, &Outputs, &Setpoints, Kps, Kis, Kds, DIRECT);
double Kpk = SALTKP, Kik = SALTKI, Kdk = SALTKD;
PID myPIDK(&Inputk, &Outputk, &Setpointk, Kpk, Kik, Kdk, DIRECT);

float A2Conc = 0;
float A0Conc = 0;
float saltConcA0 = 0;
float saltConcA2 = 0;
float waterConcA0 = 0;
float waterConcA2 = 0;
bool kidLoaded=False;
bool sphLoaded=False;
unsigned long runStart;
unsigned long flushStart;
unsigned long calibrationStart;
double testTime;
double initialActivity = 0.0;
double upperBoundTracer;
double lowerBoundTracer;

int state = 5;
int numRowsk = 0;
int numRowss = 0;
double curveSph[MAX_ROWS][2] = { { 0.0, UPPER_SETPOINT }, { 60.0, 0.0 } };
double curveKid[MAX_ROWS][2] = { { 0.0, UPPER_SETPOINT }, { 60.0, 0.0 } };
int curveIndexk = 0;
int curveIndexs = 0;
int waterCommandk;
int waterCommands;

String receivedString;
String inChar;

unsigned long currentTime = millis();

double kidneyGains[2][3] = { { 0.07, 0.1, 0.005 }, { 0.05, 0.5, 0.005 } };
double sphereGains[2][3] = { { 0.1, 0.4, 0.01 }, { 0.04, 0.14, 0.005 }};

void setup() {
  pinMode(WATERK, OUTPUT);
  pinMode(SALTK, OUTPUT);
  pinMode(WATERS, OUTPUT);
  pinMode(SALTS, OUTPUT);

  Inputs = analogRead(A0);
  Inputk = analogRead(A2);

  Serial.begin(115200);

  myPIDs.SetMode(MANUAL);
  myPIDs.SetSampleTime(8);
  myPIDs.SetControllerDirection(DIRECT);
  myPIDs.SetOutputLimits(SALT_MIN, 255);
  myPIDk.SetMode(MANUAL);
  myPIDk.SetSampleTime(8);
  myPIDk.SetControllerDirection(DIRECT);
  myPIDk.SetOutputLimits(SALT_MIN, 255);


  state = STOP;  // change this to be in the Stopped State once GUI is fully done
}

void loop() {


  for (int i = 0; i < WINDOW_SIZE; i++) {
    A2Conc += analogRead(A2);
    A0Conc += analogRead(A0);

  }
  A2Conc = A2Conc / WINDOW_SIZE;
  A0Conc = A0Conc / WINDOW_SIZE;

  if (state == RUN) {

    // if(currentTime-runStart<=RAMP_TIME){
    //   Setpoint = curve[0][1];
    //   currentTime = millis();
    // }
    
    
    
    /*currentTime = millis();
    if (currentTime - runStart >= (int)curve[curveIndex + 1][0] * 1000) {
      curveIndex++;
    }
    */
    if(kidLoaded==True){
    Setpointk = curveKid[curveIndexk][1];

    //  unsigned long setpointTime = millis();
    //  Setpoint = 140.0 * exp(-0.005*(double)(setpointTime-currentTime)/1000.0);


    if (curveIndexk >= numRowsk) {
      state = STOP;  // MAYBE HAVE A MESSAGE THAT PRINTS OUT THE PROFILE HAS BEEN COMPLETED
      Serial.println("Finished... Stopping...");
      curveIndexk = 0;
    }

    Inputk = A2Conc;
    //myPID.SetSampleTime(8);
    waterCommandk = (int)linearInterpolation(Setpointk, LOWER_SETPOINT, UPPER_SETPOINT, 250, WATER_MIN);
    analogWrite(WATERk, waterCommandk);

    Kpk = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][0], kidneyGains[1][0]);
    Kik = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][1], kidneyGains[1][1]);
    Kdk = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][2], kidneyGains[1][2]);
    // Kp = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][0], sphereGains[1][0]);
    // Ki = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][1], sphereGains[1][1]);
    // Kd = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][2], sphereGains[1][2]);
    // //Serial.print(0);
    myPIDK.SetTunings(Kpk, Kik, Kdk);

    myPIDK.Compute();
    analogWrite(SALTK, (int)Outputk);
    }
    if(sphLoaded==True){
    Setpoints = curveSph[curveIndexs][1];

    //  unsigned long setpointTime = millis();
    //  Setpoint = 140.0 * exp(-0.005*(double)(setpointTime-currentTime)/1000.0);


    if (curveIndexs >= numRowss) {
      state = STOP;  // MAYBE HAVE A MESSAGE THAT PRINTS OUT THE PROFILE HAS BEEN COMPLETED
      Serial.println("Finished... Stopping...");
      curveIndexs = 0;
    }

    Inputs = A0conc;
    //myPID.SetSampleTime(8);
    waterCommands = (int)linearInterpolation(Setpoints, LOWER_SETPOINT, UPPER_SETPOINT, 250, WATER_MIN);
    analogWrite(WATERS, waterCommands);

    Kps = linearInterpolation(Setpoints, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][0], kidneyGains[1][0]);
    Kis = linearInterpolation(Setpoints, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][1], kidneyGains[1][1]);
    Kds = linearInterpolation(Setpoints, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][2], kidneyGains[1][2]);
    // Kp = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][0], sphereGains[1][0]);
    // Ki = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][1], sphereGains[1][1]);
    // Kd = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][2], sphereGains[1][2]);
    // //Serial.print(0);
    myPIDS.SetTunings(Kps, Kis, Kds);

    myPIDS.Compute();
    analogWrite(SALTS, (int)Outputs);
    }
    testTime = (double)(millis()-runStart)/1000.0;
    // Serial.print(time);
    // Serial.print(" ");
    Serial.print(0);
    Serial.print(" ");
    Serial.print(Setpoint);
    Serial.print(" ");
    Serial.print(A2Conc);
    Serial.print(" ");
    // Serial.print(0);
    // Serial.print(" ");
    Serial.print(waterCommand);
    Serial.print(" ");
    Serial.print((int)Output);
    Serial.print(" ");
    Serial.print(Setpoint * 1.1);
    Serial.print(" ");
    Serial.println(Setpoint * 0.9);
  }

  else if (state == FLUSH) {
    Serial.println("flush");


    analogWrite(WATER, FULL_SPEED);
    analogWrite(SALT, FULL_SPEED);

    
    delay(10000);
    Serial.println(analogRead(CONCENTRATION_OUTLET));
    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);
    Serial.println("Done Flush");
    state = STOP;
  }
  else if (state == CALIBRATE) {
    Serial.println("calibrate");
    if(kidLoaded==True){
    analogWrite(WATERK, FULL_SPEED);
    analogWrite(SALTK, OFF);
    }
    if(sphLoaded==True){
    analogWrite(WATERS, FULL_SPEED);
    analogWrite(SALTS, OFF);
    }
   
    delay(CALIBRATION_TIME);
    if(kidLoaded==True){
    analogWrite(WATERK, OFF);
    analogWrite(SALTK, OFF);
    }
    if(sphLoaded==True){
    analogWrite(WATERS, OFF);
    analogWrite(SALTS, OFF);
    }

    delay(1000);
    if(kidLoaded==True){
    for (int i = 0; i < 50; i++) {
      waterConcA0 += analogRead(A0);
    }
    waterConcA0 = waterConcA0 / 50;
    }
    if(sphLoaded==True){
          for (int i = 0; i < 50; i++) {
      waterConcA2 += analogRead(A0);
    }
    waterConcA2 = waterConcA0 / 50;
    }
    
    analogWrite(WATER, OFF);
    analogWrite(SALT, FULL_SPEED);
    
    delay(CALIBRATION_TIME);
    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);

    delay(1000);

    if(kidLoaded==True){
    for (int i = 0; i < 50; i++) {
      saltConcA0 += analogRead(A0);
    }
    saltConcA0 = saltConcA0 / 50;
    }
    if(sphLoaded==True){
          for (int i = 0; i < 50; i++) {
      saltConcA2 += analogRead(A0);
    }
    saltConcA2 = saltConcA0 / 50;
    }

    Serial.println(saltConcA0);
    Serial.println(saltConcA2);
    Serial.println(waterConc);
    Serial.println(waterConc);


    state = STOP;
  }
  if (state == CURVELOADSPH) {
    Serial.println("curveload");
    analogWrite(WATERS, OFF);
    analogWrite(SALTS, OFF);
    while (Serial.available()==0) {
    }
    if (Serial.available() > 0) {
      // Serial.readBytes((char*)&numRows, numRowsSize); // Read numRows as an int
      receivedString = Serial.readStringUntil('\n');
      Serial.println("Received numRows: " + receivedString);
      numRowss = receivedString.toInt();

      // Define the 2D array to store received data
      // Convert bytes back into 2D list of doubles
      for (int i = 0; i < numRowss; i++) {
        for (int j = 0; j < 2; j++) {
          while (!Serial.available()) {
          }
          receivedString = Serial.readStringUntil('\n');
          //Serial.println(receivedString);
          //Serial.println(receivedString);
          curveSph[i][j] = receivedString.toFloat();
          //Serial.println(curve[i][j]);
        }
      }
      Serial.println("Finished Loading Curve");
      for (int i = 0; i < numRows; i++) {
        Serial.print("Row ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(curveSph[i][0]);
        Serial.print(", ");
        Serial.println(curveSph[i][1]);
      }
    }
    sphLoaded=True;
    state = STOP;
  }
  if (state == CURVELOADKID) {
    Serial.println("curveload");
    analogWrite(WATERK, OFF);
    analogWrite(SALTK, OFF);
    while (Serial.available()==0) {
    }
    if (Serial.available() > 0) {
      // Serial.readBytes((char*)&numRows, numRowsSize); // Read numRows as an int
      receivedString = Serial.readStringUntil('\n');
      Serial.println("Received numRows: " + receivedString);
      numRowsk = receivedString.toInt();

      // Define the 2D array to store received data
      // Convert bytes back into 2D list of doubles
      for (int i = 0; i < numRowsk; i++) {
        for (int j = 0; j < 2; j++) {
          while (!Serial.available()) {
          }
          receivedString = Serial.readStringUntil('\n');
          //Serial.println(receivedString);
          //Serial.println(receivedString);
          curveKid[i][j] = receivedString.toFloat();
          //Serial.println(curve[i][j]);
        }
      }
      Serial.println("Finished Loading Curve");
      for (int i = 0; i < numRowsk; i++) {
        Serial.print("Row ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(curveKid[i][0]);
        Serial.print(", ");
        Serial.println(curveKid[i][1]);
      }
    }
    kidLoaded=True;
    state = STOP;
  }

  else if (state == STOP) {

    myPID.SetMode(MANUAL);
    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);
  }
  else if (state == SALT_MEASURE) {
    // analogWrite(WATER, 120);
    // analogWrite(SALT, 120);
    Serial.print(A0Conc);
    Serial.print(" ");
    Serial.println(A2Conc);
  }



  if (Serial.available() > 0) {


    // read incoming serial data:

    inChar = Serial.readStringUntil('\n');
    //Serial.println(inChar);

    if (inChar.equals("1")) {
      state = RUN;
      //Serial.println("About to start...");
      myPID.SetMode(AUTOMATIC);
      runStart = millis();
      currentTime = millis();
      curveIndex = 0;
      while (!Serial.available()) {
      }
      if (Serial.available() > 0) {
        receivedString = Serial.readStringUntil('\n');
        
        initialActivity = receivedString.toDouble();
        lowerBoundTracer = linearInterpolation(LOWER_SETPOINT,saltConc,waterConc,initialActivity, 0);
      }
       
    } else if (inChar.equals("2")) {
      Serial.println(CALIBRATE);
      state = CALIBRATE;
    } else if (inChar.equals("3")) {
      state = FLUSH;

    } else if (inChar.equals("4")) {
      // Serial.println(CURVELOAD);
      state = CURVELOAD;
    } else if (inChar.equals("5")) {
      Serial.println("Stopping");
      state = STOP;
    }

    else if (inChar.equals("6")) {
      Serial.println(myPID.GetKp(), 3);
      Serial.println(myPID.GetKi(), 3);
      Serial.println(myPID.GetKd(), 3);
    }

    else if (inChar.equals("7")) {
      Serial.println("Changing Gains");
      double tempKp, tempKi, tempKd;
      while (!Serial.available()) {
      }
      if (Serial.available() > 0) {
        receivedString = Serial.readStringUntil('\n');
        Serial.println(receivedString);
        tempKp = receivedString.toDouble();
      }
      while (!Serial.available()) {
      }
      if (Serial.available() > 0) {
        receivedString = Serial.readStringUntil('\n');
        Serial.println(receivedString);
        tempKi = receivedString.toDouble();
      }
      while (!Serial.available()) {
      }
      if (Serial.available() > 0) {
        receivedString = Serial.readStringUntil('\n');
        Serial.println(receivedString);
        tempKd = receivedString.toDouble();
      }
      Kp = tempKp;
      Ki = tempKi;
      Kd = tempKd;
      myPID.SetTunings(Kp, Ki, Kd);

      Serial.println("Done Changing Gains");
    }

    else if (inChar.equals("8")) {
      Serial.println("Changing Setpoint...");
      double tempSet;
      while (!Serial.available()) {
      }
      if (Serial.available() > 0) {
        receivedString = Serial.readStringUntil('\n');
        Serial.println(receivedString);
        tempSet = receivedString.toDouble();
      }
      curve[0][1] = tempSet;
      Serial.println(curve[0][1]);
      Serial.println("Done Changing Setpoint..");
    } 
    
    else if (inChar.equals("9")) {
      Serial.println("Measuring Salt...");
      delay(10);
      state = SALT_MEASURE;
    }
  }
}

int map_range(float value, float old_min, float old_max, float new_min, float new_max) {
  // Scale the value from the old range to a value in the range [0, 1]
  float normalized_value = (value - old_min) / (old_max - old_min);
  // Map this normalized value to the new range
  int new_value = new_min + normalized_value * (new_max - new_min);
  return new_value;
}

double linearInterpolation(float x, float x1, float x0, float y1, float y0) {
  float normalized_Value = (y1 - y0) / (x1 - x0) * (x - x0) + y0;
  return (double)normalized_Value;
}