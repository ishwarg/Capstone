#include <PID_v1.h>





//Define Variables we'll be connecting to
double Setpoint, Input, Output;

//Specify the links and initial tuning parameters
double Kp=40, Ki=20, Kd=0;
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





void setup() {
  // put your setup code here, to run once:
  Input = analogRead(0);
  Setpoint = 38;
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);
  pinMode(3, OUTPUT);
  digitalWrite(3, LOW);
  Serial.begin(9600);

  // initialize control over the keyboard:


  // analogWrite(5, 70);
  // analogWrite(3, 150);
  myPID.SetMode(AUTOMATIC);
  analogWrite(5, 85);

}

void loop() {
  // put your main code here, to run repeatedly:
  
  //
  //
  // CONCENTRATION SENSOR CODE
  //
  //

  for(int i =0; i<50;i++){
    conc += analogRead(0);
    
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
  
  

  
  Input = conc;
  myPID.Compute();
  if (Output> 255)
  Output = 255;
  if (Output<0){
    Output = 0;
  }
  Serial.println((int)conc);
 
  analogWrite(3, (int)Output);
  delay(90);



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
  
    if (inChar == 'w'){
      Serial.println("received");

      while(Serial.available()== 0){

      }
      Serial.println("Changing...");

      highSpeed = Serial.parseInt();
      Serial.println(highSpeed);

      if (highSpeed <255&&highSpeed>=0)
      analogWrite(5, highSpeed );

    }
    if (inChar == 's'){
      Serial.println("received");

      while(Serial.available()== 0){

      }
      Serial.println("Changing...");

      Setpoint = (double)Serial.parseInt();
      Serial.println(highSpeed);

      if (highSpeed <255&&highSpeed>=0)
      analogWrite(5, highSpeed );

    }

  }

  

}
