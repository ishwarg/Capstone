#include <PID_v1.h>

#define WATERK 4
#define SALTK 2
#define WATERS 10
#define SALTS 7
#define KIDNEY_CONC 4
#define SPHERE_CONC 2
#define RESEVOIR 7

#define RUN 1
#define CALIBRATE 2
#define FLUSH 3
#define CURVELOADSPH 10
#define CURVELOADKID 11
#define STOP 5
#define SALT_MEASURE 9

#define CALIBRATION_TIME 20000
#define FLUSH_TIME 10000
#define MAX_ROWS 300
#define RAMP_TIME 20000

#define FULL_SPEED 255
#define OFF 0

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

float kidneyConc = 0;
float sphereConc = 0;

float saltConcSphere = 0;
float saltConcKidney = 5;
float waterConcSphere = 0;
float waterConcKidney = 0;

bool kidLoaded=0;
bool sphLoaded=0;
unsigned long runStart;
unsigned long flushStart;
unsigned long calibrationStart;
double testTime;
double initialActivity = 0.0;
double upperBoundTracer;
double lowerBoundTracers;
double lowerBoundTracerk;

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

double kidneyGains[2][3] = {{0.5,0.2,0.01 }, {0.25,0.1,0.01}};
double sphereGains[2][3] = { { 0.5,0.5,0.01 }, {0.25,0.4,0.01}};

void setup() {
  pinMode(WATERK, OUTPUT);
  pinMode(SALTK, OUTPUT);
  pinMode(WATERS, OUTPUT);
  pinMode(SALTS, OUTPUT);


  Serial.begin(115200);

  myPIDS.SetMode(MANUAL);
  myPIDS.SetSampleTime(8);
  myPIDS.SetControllerDirection(DIRECT);
  myPIDS.SetOutputLimits(SALT_MIN, 255);

  myPIDK.SetMode(MANUAL);
  myPIDK.SetSampleTime(8);
  myPIDK.SetControllerDirection(DIRECT);
  myPIDK.SetOutputLimits(SALT_MIN, 255);


  state = STOP;  // change this to be in the Stopped State once GUI is fully done
}

void loop() {


  for (int i = 0; i < WINDOW_SIZE; i++) {
    kidneyConc += analogRead(KIDNEY_CONC);
    sphereConc += analogRead(SPHERE_CONC);

  }
  kidneyConc = kidneyConc / WINDOW_SIZE;
  sphereConc = sphereConc / WINDOW_SIZE;
  kidneyConc = linearInterpolation(kidneyConc, saltConcKidney, waterConcKidney, initialActivity, 0);
  sphereConc = linearInterpolation(sphereConc, saltConcSphere, waterConcSphere, initialActivity, 0);

  if (state == RUN) {

    currentTime = millis();
    
    if(kidLoaded==1){
      if (currentTime - runStart >= (int)curveKid[curveIndexk + 1][0] * 1000) {
      curveIndexk++;
      }

      if (curveIndexk >= numRowsk) {
      state = STOP;  // MAYBE HAVE A MESSAGE THAT PRINTS OUT THE PROFILE HAS BEEN COMPLETED
      Serial.println("Finished Kidneys");
      Serial.println(numRowsk);
      curveIndexk = 0;
      }

      Setpointk = curveKid[curveIndexk][1];
      Inputk = kidneyConc;
     
      waterCommandk = (int)linearInterpolation(Setpointk, LOWER_SETPOINT, UPPER_SETPOINT, 250, WATER_MIN);
      analogWrite(WATERK, waterCommandk);

      Kpk = linearInterpolation(Setpointk, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][0], kidneyGains[1][0]);
      Kik = linearInterpolation(Setpointk, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][1], kidneyGains[1][1]);
      Kdk = linearInterpolation(Setpointk, UPPER_SETPOINT, LOWER_SETPOINT, kidneyGains[0][2], kidneyGains[1][2]);
      // Kp = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][0], sphereGains[1][0]);
      // Ki = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][1], sphereGains[1][1]);
      // Kd = linearInterpolation(Setpoint, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][2], sphereGains[1][2]);
      // //Serial.print(0);
      myPIDK.SetTunings(Kpk, Kik, Kdk);

      myPIDK.Compute();
      analogWrite(SALTK, (int)Outputk);
    }

    if(sphLoaded==1){
      if (currentTime - runStart >= (int)curveKid[curveIndexs + 1][0] * 1000) {
      curveIndexs++;
      }

      if (curveIndexs >= numRowss) {
        state = STOP;  // MAYBE HAVE A MESSAGE THAT PRINTS OUT THE PROFILE HAS BEEN COMPLETED
        Serial.println("Finished Spheres");
        Serial.println(numRowss);
        curveIndexs = 0;
      }
      Setpoints = curveSph[curveIndexs][1];
      Inputs = sphereConc;
    
      waterCommands = (int)linearInterpolation(Setpoints, LOWER_SETPOINT, UPPER_SETPOINT, 250, WATER_MIN);
      analogWrite(WATERS, waterCommands);

    
      Kps = linearInterpolation(Setpoints, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][0], sphereGains[1][0]);
      Kis = linearInterpolation(Setpoints, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][1], sphereGains[1][1]);
      Kds = linearInterpolation(Setpoints, UPPER_SETPOINT, LOWER_SETPOINT, sphereGains[0][2], sphereGains[1][2]);
      //Serial.print(0);
      myPIDS.SetTunings(Kps, Kis, Kds);

      myPIDS.Compute();
      analogWrite(SALTS, (int)Outputs);

    }

    testTime = (double)(millis()-runStart)/1000.0;

    Serial.print(testTime);
    Serial.print(" ");
    if (sphLoaded == 1 && kidLoaded == 1){
      Serial.print(sphereConc,5);
      Serial.print(" ");
      Serial.print(Setpoints,5);
      Serial.print(" ");
      Serial.print(kidneyConc,5);
      Serial.print(" ");
      Serial.println(Setpointk,5);
  
      
    
    }
    else if (sphLoaded == 1){
      Serial.print(sphereConc,5);
      Serial.print(" ");
      Serial.println(Setpoints,5);
    }
    else{
      // Serial.print(Setpointk);
      // Serial.print(" ");
      Serial.print(kidneyConc,5);
      Serial.print(" ");
      Serial.println(Setpointk,5);
    }

    // Serial.print(0);
    // Serial.print(" ");
    // Serial.print(Setpointk);
    // Serial.print(" ");
    // Serial.print(kidneyConc);
    // Serial.print(" ");
    // Serial.print(0);
    // Serial.print(" ");
    // Serial.print(waterCommandk);
    // Serial.print(" ");
    // Serial.print((int)Outputk);
    // Serial.print(" ");
    // Serial.print(Setpointk * 1.1);
    // Serial.print(" ");
    // Serial.println(Setpointk * 0.9);
    
  }

  else if (state == FLUSH) {
    Serial.println("flush");


    analogWrite(WATERS, FULL_SPEED);
    analogWrite(SALTS, FULL_SPEED);

    
    delay(10000);
    Serial.println(analogRead(SPHERE_CONC));
    analogWrite(WATERS, OFF);
    analogWrite(SALTS, OFF);
    Serial.println("Done Flush");
    state = STOP;
  }

  else if (state == CALIBRATE) {
    Serial.println("calibrate");

    
    analogWrite(WATERK, FULL_SPEED);
    analogWrite(SALTK, OFF);
    

    
    analogWrite(WATERS, FULL_SPEED);
    analogWrite(SALTS, OFF);
    
   
    delay(CALIBRATION_TIME);

    
    analogWrite(WATERK, OFF);
    analogWrite(SALTK, OFF);
    
    
    analogWrite(WATERS, OFF);
    analogWrite(SALTS, OFF);
    

    delay(1000);
    
    for (int i = 0; i < 50; i++) {
      waterConcSphere += (float)analogRead(SPHERE_CONC);
    
    waterConcSphere = waterConcSphere / 50.0;
    }
    
    for (int i = 0; i < 50; i++) {
      waterConcKidney += (float)analogRead(KIDNEY_CONC);
    }
    waterConcKidney = waterConcKidney / 50.0;
    
    
    
    analogWrite(WATERK, OFF);
    analogWrite(SALTK, FULL_SPEED);
    
    
    analogWrite(WATERS, OFF);
    analogWrite(SALTS, FULL_SPEED);
    
    
    delay(CALIBRATION_TIME);
    
    
    analogWrite(WATERK, OFF);
    analogWrite(SALTK, OFF);
    
    
    analogWrite(WATERS, OFF);
    analogWrite(SALTS, OFF);
    

    delay(1000);

    
    for (int i = 0; i < 50; i++) {
      saltConcSphere += (float)analogRead(SPHERE_CONC);
    }
    saltConcSphere = saltConcSphere / 50.0;
    
    
    for (int i = 0; i < 50; i++) {
      saltConcKidney += (float)analogRead(KIDNEY_CONC);
    }
    saltConcKidney = saltConcKidney / 50.0;
    

    Serial.print(saltConcSphere);
    Serial.print(" ");
    Serial.print(saltConcKidney);
    Serial.print(" ");
    Serial.print(waterConcSphere);
    Serial.print(" ");
    Serial.println(waterConcKidney);


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
      Serial.println("Received Sphere numRows: " + receivedString);
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
      for (int i = 0; i < numRowss; i++) {
        Serial.print("Row ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(curveSph[i][0]);
        Serial.print(", ");
        Serial.println(curveSph[i][1]);
      }
    }
    sphLoaded=1;
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
      Serial.println("Received Kidney numRows: " + receivedString);
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
    kidLoaded=1;
    state = STOP;
  }

  else if (state == STOP) {

    myPIDS.SetMode(MANUAL);
    myPIDK.SetMode(MANUAL);
    analogWrite(WATERK, OFF);
    analogWrite(SALTK, OFF);
    analogWrite(WATERS, OFF);
    analogWrite(SALTS, OFF);
  }
  else if (state == SALT_MEASURE) {
    // analogWrite(WATER, 120);
    // analogWrite(SALT, 120);
    // Serial.print(analogRead(SPHERE_CONC));
    // Serial.print(" ");
    // Serial.println(analogRead(KIDNEY_CONC));
    Serial.println(analogRead(RESEVOIR));
  }



  if (Serial.available() > 0) {


    // read incoming serial data:

    inChar = Serial.readStringUntil('\n');
    //Serial.println(inChar);

    if (inChar.equals("1")) {
      state = RUN;
      //Serial.println("About to start...");
      if (kidLoaded == 1)
        myPIDK.SetMode(AUTOMATIC);
      if (sphLoaded == 1)
        myPIDS.SetMode(AUTOMATIC);
      runStart = millis();
      currentTime = millis();
      curveIndexk = 0;
      curveIndexs = 0;
      while (!Serial.available()) {
      }
      if (Serial.available() > 0) {
        receivedString = Serial.readStringUntil('\n');
        
        initialActivity = receivedString.toDouble();
        lowerBoundTracers = linearInterpolation(LOWER_SETPOINT,saltConcSphere,waterConcSphere,initialActivity, 0);
        lowerBoundTracerk = linearInterpolation(LOWER_SETPOINT,saltConcKidney,waterConcKidney,initialActivity, 0);
      }
       
    } else if (inChar.equals("2")) {
      Serial.println(CALIBRATE);
      state = CALIBRATE;
    } else if (inChar.equals("3")) {
      state = FLUSH;

    } else if (inChar.equals("10")) {
      // Serial.println(CURVELOAD);
      state = CURVELOADSPH;
    } 
    else if (inChar.equals("11")) {
      // Serial.println(CURVELOAD);
      state = CURVELOADKID;
    }
    else if (inChar.equals("5")) {
      Serial.println("Stopping");
      state = STOP;
      sphLoaded = 0;
      sphLoaded = 0;
    }

    else if (inChar.equals("6")) {
      Serial.println(myPIDS.GetKp(), 3);
      Serial.println(myPIDS.GetKi(), 3);
      Serial.println(myPIDS.GetKd(), 3);
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
      // Kps = tempKp;
      // Ki = tempKi;
      // Kd = tempKd;
      // myPID.SetTunings(Kp, Ki, Kd);

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
      // curve[0][1] = tempSet;
      // Serial.println(curve[0][1]);
      // Serial.println("Done Changing Setpoint..");
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
