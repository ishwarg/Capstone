#include <PID_v1.h>

#define WATER 3
#define SALT 8  
#define CONCENTRATION 1

//Define Variables we'll be connecting to
double Setpoint, Inputs, Outputs;
double  Inputw, Outputw;
//Specify the links and initial tuning parameters
double Kps, Kis, Kds;
double Kpw, Kiw, Kdw;
PID myPIDs(&Inputs, &Outputs, &Setpoint, Kps, Kis, Kds, DIRECT);
PID myPIDw(&Inputw, &Outputw, &Setpoint, Kpw, Kiw, Kdw, REVERSE);

int maxpoint;

double time = 0;
float conc = 0;
int begin;
int state = 0;

void setup() {
  // put your setup code here, to run once:
  begin = millis();  //beginning the timer for when the code starts
  Setpoint = 0;  //initial target concentration; will be changed when the calibration curve is loaded in
  maxpoint = 100;
  Setpoint = maxpoint;

  pinMode(WATER, OUTPUT);

  pinMode(SALT, OUTPUT);

  Serial.begin(9600);
  myPIDs.SetMode(AUTOMATIC);
  myPIDs.SetOutputLimits(55,255);
  myPIDs.SetSampleTime(23);
  myPIDw.SetMode(MANUAL);
  myPIDw.SetOutputLimits(55,255);
  analogWrite(WATER, 0);
  analogWrite(SALT, 0);
  // analogWrite(WATER, 0);
  // analogWrite(SALT,0);

}

void loop() {
  begin = millis();
  for(int i =0; i<50;i++){
    conc += analogRead(A1);
    
  }
  conc = conc/50;

  // if (millis()-begin>10000){
  //   Setpoint = maxpoint*exp(-1*double(millis()-begin)/100000.0);  //REPLACE WITH ACTUAL INPUT CURVE CODE
  // }
  if( Setpoint <= 60) {
    myPIDs.SetMode(MANUAL);
    myPIDs.SetOutputLimits(55,255);
    myPIDw.SetMode(AUTOMATIC);
    myPIDw.SetOutputLimits(55,255);
  }

  if ( (Setpoint <= 135) && (Setpoint > 100) ) {
    Inputw = conc;
    myPIDw.SetTunings(5,3,0.0);
    myPIDw.SetTunings(5,3,0.0);
    analogWrite(SALT,255);
    myPIDw.Compute();
    analogWrite(WATER, (int)Outputw);
  }
  // else if ( (Setpoint <= 100) && (Setpoint > 60) ) {
  //   Inputs = conc;
  //   myPIDs.SetTunings(0.5,0.9,0.01);
  //   analogWrite(WATER, 120);
  //   myPIDs.Compute();
  //   analogWrite(SALT, (int)Outputs);
  // }
  else if ( (Setpoint <= 100) && (Setpoint > 60) ) {
    Inputs = conc;
    myPIDs.SetTunings(40.46,19.91,0.0);
    analogWrite(WATER, 120);
    myPIDs.Compute();
    analogWrite(SALT, (int)Outputs);
  }
  else if ( (Setpoint <= 60) && (Setpoint > 50) ){
    Inputw = conc;
    myPIDw.SetTunings(0.15,0.35,0.01);
    analogWrite(SALT,120);
    myPIDw.Compute();
    analogWrite(WATER, (int)Outputw);
  }
  else if ( (Setpoint <= 25) && (Setpoint > 0) ){
    Inputw = conc;
    myPIDw.SetTunings(0.05,0.2,0.03);
    analogWrite(SALT,85);
    myPIDw.Compute();
    analogWrite(WATER, (int)Outputw);
  }

    Serial.print(0);
    Serial.print(" ");
    Serial.print(Setpoint-(Setpoint/10));
    Serial.print(" ");
    Serial.print(Setpoint);
    Serial.print(" ");
    Serial.print(Setpoint+(Setpoint/10));
    Serial.print(" ");
    Serial.println((int)(conc));
    Serial.print(Setpoint+(Setpoint/10));
    Serial.print(" ");
    // Serial.println((int)(conc-Setpoint)/Setpoint*100);
    

    delay(5);
  
    
 

  }

  

