#include <PID_v1.h>

#define WATER 5
#define SALT 6
#define CONCENTRATION 0

#define RUN 1
#define CALIBRATE 2
#define FLUSH 3
#define CURVELOAD 4
#define PAUSE 5
#define STOP 6

//Define Variables we'll be connecting to
double Setpoint, Input, Output;

//Specify the links and initial tuning parameters
double Kp=2.3, Ki=1.5, Kd=0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);


int lowSpeed = 0;
int highSpeed = 0;

int prevSig = 0;
int newSig = 0;
double freq = 0.0;
double flow = 0;
bool state = false;
double time = 0;
float conc = 0;
int begin;
int state = 0;


void setup() {
  // put your setup code here, to run once:
  begin = millis();  //beginning the timer for when the code starts
  Input = analogRead(CONCENTRATION);
  Setpoint = 20;  //initial target concentration; will be changed when the calibration curve is loaded in
  
  pinMode(WATER, OUTPUT);
  digitalWrite(WATER, LOW);

  pinMode(SALT, OUTPUT);
  digitalWrite(SALT, LOW);

  Serial.begin(9600);
  myPID.SetMode(AUTOMATIC);

  analogWrite(WATER, 65);
  state = RUN;

}

void loop() {

  for(int i =0; i<50;i++){
    conc += analogRead(0);
    
  }
  conc = conc/50;
  
  
/*  FLOW METER CODE


  if (newSig-prevSig>100 && !state){
    time = micros();
    state = true; 
  }
  
  if (newSig-prevSig<100 && state){
    time = micros()-time;
    time = time/1000000;
    
    state = false;
    freq = 1.0/time/2.0;

    flow = freq/38;
  }
  
  */

  switch (state) {
    case RUN:
      if (millis()-begin>10000){
        Setpoint = 20.0*exp(-1*double(millis()-begin)/100000.0);  //REPLACE WITH ACTUAL INPUT CURVE CODE
      }

      Input = conc;
      myPID.Compute(); //change code so that there is saturation from the PID object itself
      if (Output> 255)
      Output = 255;
      if (Output<0){
        Output = 0;
      }


      Serial.print(0);
      Serial.print(" ");
      Serial.print(25);
      Serial.print(" ");
      Serial.print(Setpoint);
      Serial.print(" ");
      Serial.println((int)(conc));
      // Serial.println((int)(conc-Setpoint)/Setpoint*100);
    
      analogWrite(6, (int)Output);
      delay(5);
  
      break;
    case CALIBRATE:
    
      break;
    case FLUSH:

      break;
    
    case CURVELOAD:

      break;
    
    case PAUSE:

      break;
    case STOP:


      break;

    }

  if (Serial.available() > 0) {

    // read incoming serial data:
    
    char inChar = Serial.read();
    if (inChar == 'q'){
      Serial.println("received");

      while(Serial.available()== 0){

      }
      Serial.println("Changing...");
      lowSpeed = Serial.parseInt();
      Serial.println(lowSpeed);
      if (lowSpeed <255&&lowSpeed>=0)
      analogWrite(3, lowSpeed );

    }
  

  }

  

}
