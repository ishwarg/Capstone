#include <PID_v1.h>

#define WATER 5
#define SALT 6
#define CONCENTRATION 0

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


void setup() {
  // put your setup code here, to run once:
  begin = millis();
  Input = analogRead(CONCENTRATION);
  Setpoint = 20;
  
  pinMode(WATER, OUTPUT);
  digitalWrite(WATER, LOW);

  pinMode(SALT, OUTPUT);
  digitalWrite(SALT, LOW);

  Serial.begin(9600);
  myPID.SetMode(AUTOMATIC);

  analogWrite(5, 65);

}

void loop() {
  // put your main code here, to run repeatedly:
  
  //
  //
  // CONCENTRATION SENSOR CODE
  //
  //

  for(int i =0; i<50;i++){
    conc += analogRead(CONCENTRATION);
    
  }
  conc = conc/50;
  

  //
  //
  // FLOW METER CODE
  //
  //


  // if (newSig-prevSig>100 && !state){
  //   time = micros();
  //   state = true; 
  // }
  
  // if (newSig-prevSig<100 && state){
  //   time = micros()-time;
  //   time = time/1000000;
    
  //   state = false;
  //   freq = 1.0/time/2.0;

  //   flow = freq/38;
  // }
  
  

  if (millis()-begin>10000){
    Setpoint = 20.0*exp(-1*double(millis()-begin)/100000.0);
  }
  Input = conc;
  myPID.Compute();
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
 
  analogWrite(SALT, (int)Output);
  delay(5);
  


  if (Serial.available() > 0) {

    // read incoming serial data:
    
    char inChar = Serial.read();
    if (inChar == 'a'){
      Serial.println("Waiting to set water speed...");

      while(Serial.available()== 0){

      }
      Serial.println("Changing...");
      lowSpeed = Serial.parseInt();
      Serial.println(lowSpeed);
      if (lowSpeed <255&&lowSpeed>=0)
        analogWrite(WATER, lowSpeed );
      else
        analogWrite(WATER, lowSpeed);
      

      

    
    }

  }

  

}
