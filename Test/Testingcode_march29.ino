#define WATER 3
#define SALT 9
#define CONCENTRATION 1
int conc = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(WATER, OUTPUT);

  pinMode(SALT, OUTPUT);

  pinMode(CONCENTRATION,INPUT);

  Serial.begin(9600);
 // myPID.SetMode(AUTOMATIC);

  analogWrite(WATER,120);
  analogWrite(SALT,100);

}

void loop() {
  // put your main code here, to run repeatedly:
  for(int i =0; i<50;i++){
    conc += analogRead(CONCENTRATION);
    
  }
  conc = conc/50;

  Serial.print(0);
  Serial.print(" ");
  Serial.println(int(conc));
  delay(5);

}
