#include <PID_v1.h>

#define WATER 5
#define SALT 6
#define CONCENTRATION 0

#define RUN 1
#define CALIBRATE 2
#define FLUSH 3
#define CURVELOAD 4
#define STOP 5

#define CALIBRATION_TIME 10000
#define FLUSH_TIME 10000
#define MAX_ROWS 900
#define RAMP_TIME 10000

#define FULL_SPEED 255
#define OFF 0
#define WATER_SPEED 65

double Setpoint, Input, Output;

double Kp = 2.3, Ki = 1.5, Kd = 0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

int lowSpeed = 0;
int highSpeed = 0;

int prevSig = 0;
int newSig = 0;
double freq = 0.0;
double flow = 0;
double time = 0;

float conc = 0;
float salt_conc = 0;
float water_conc = 0;

int begin;
int runStart;
int state = 0;
bool flowState = false;
int numRows = 0;
double curve[MAX_ROWS][2];
int curveIndex = 0;

void setup()
{

  Input = analogRead(CONCENTRATION);
  Setpoint = 20; // initial target concentration; will be changed when the calibration curve is loaded in

  pinMode(WATER, OUTPUT);
  digitalWrite(WATER, LOW);

  pinMode(SALT, OUTPUT);
  digitalWrite(SALT, LOW);

  Serial.begin(9600);
  myPID.SetMode(MANUAL);

  analogWrite(WATER, WATER_SPEED);
  state = RUN;      // change this to be in the Stopped State once GUI is fully done
  begin = millis(); // beginning the timer for when the code starts
}

void loop()
{

  for (int i = 0; i < 50; i++)
  {
    conc += analogRead(0);
  }
  conc = conc / 50;
  Serial.print(0);
  Serial.print(" ");
  Serial.print(25);
  Serial.print(" ");
  Serial.print(Setpoint);
  Serial.print(" ");
  Serial.println((int)(conc));

  /*  FLOW METER CODE
    if (newSig-prevSig>100 && !flowstate){
      time = micros();
      flowstate = true;
    }

    if (newSig-prevSig<100 && flowstate){
      time = micros()-time;
      time = time/1000000;

      flowstate = false;
      freq = 1.0/time/2.0;

      flow = freq/38;
    }
    */

  switch (state)
  {
  case RUN:

    if (millis() - runStart < RAMP_TIME)
    {
      // Setpoint = 20.0 * exp(-1 * double(millis() - begin) / 100000.0); // REPLACE WITH ACTUAL INPUT CURVE CODE
      Setpoint = curve[0][1];

    }
    else{
      if (millis()-runStart - RAMP_TIME>(double)curve[curveIndex][0]*1000)
        curveIndex++;
      Setpoint = curve[curveIndex][1];
      
    } 

    if (curveIndex >= numRows)
      state = STOP; // MAYBE HAVE A MESSAGE THAT PRINTS OUT THE PROFILE HAS BEEN COMPLETED 
    

    Input = conc;
    myPID.Compute(); // change code so that there is saturation from the PID object itself
    if (Output > 255)
      Output = 255;
    if (Output < 0)
    {
      Output = 0;
    }

    // Serial.println((int)(conc-Setpoint)/Setpoint*100);

    analogWrite(SALT, (int)Output);
    delay(5);
    state = RUN;

    break;

  case CALIBRATE:
    int calibrationStart = millis();

    analogWrite(WATER, FULL_SPEED);
    analogWrite(SALT, OFF);

    while (millis() - calibrationStart <= CALIBRATION_TIME)
    {
    }

    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);

    delay(1000);
    for (int i = 0; i < 50; i++)
    {
      water_conc += analogRead(0);
    }
    water_conc = water_conc / 50;

    calibrationStart = millis();
    analogWrite(WATER, OFF);
    analogWrite(SALT, FULL_SPEED);

    while (millis() - calibrationStart <= CALIBRATION_TIME)
    {
    }

    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);

    delay(1000);
    for (int i = 0; i < 50; i++)
    {
      salt_conc += analogRead(0);
    }
    salt_conc = salt_conc / 50;

    state = STOP;

    break;
  case FLUSH:
    int flushStart = millis();

    analogWrite(WATER, FULL_SPEED);
    analogWrite(SALT, FULL_SPEED);

    while (millis() - flushStart <= 10000)
    {
    }
    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);
    state = STOP;
    break;

  case CURVELOAD:
    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);
    while (Serial.available()==0){

    }
    if (Serial.available() > 0)
    {
      numRows = Serial.read();

      // Define the 2D array to store received data
      for (int i = 0; i < numRows; i++)
      {
        for (int j = 0; j < 2; j++)
        { // Assuming 2 columns
          // Deserialize the received bytes into a double
          double value;
          Serial.readBytes((char *)&value, sizeof(double));
          curve[i][j] = value;
        }
      }
    }
    state = STOP;
    break;

  case STOP:
    myPID.SetMode(MANUAL);
    analogWrite(WATER, OFF);
    analogWrite(SALT, OFF);

    break;
  }
  if (Serial.available() > 0)
  {

    // read incoming serial data:

    char inChar = Serial.read();
    if (inChar == '1')
    {
      state = RUN;
      myPID.SetMode(AUTOMATIC);
      runStart = millis();
    }
    else if (inChar == '2')
      state = CALIBRATE;
    else if (inChar == '3')
      state = FLUSH;
    else if (inChar == '4')
      state = CURVELOAD;
    else if (inChar == '5')
      state = STOP;
    else
      state = STOP;
  }
}
