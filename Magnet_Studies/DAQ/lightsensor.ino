int sensorPin1 = A1;
int sensorValue1 = 1024;
int sensorPin0 = A0;
int sensorValue0 = 1024;
int sensorPin2 = A2;
int sensorValue2 = 1024;
int sensorPin3 = A3;
int sensorValue3 = 1024;
int sensorPin4 = A4;
int sensorValue4 = 1024;
int sensorPin5 = A5;
int sensorValue5 = 1024;
int lightpin1 = 13;
int lightpin2 = 9;
int lightpin3 = 5;
int lightpin4 = 12;
int lightpin5 = 8;
int lightpin6 = 4;
int lightpin7 = 7;
int lightpin8 = 2;
int lightpin9 = 3;
//String ouputstring1 = " ";
String inputstring;
bool outbool = false;
bool outbool2 = false;

void setup(void) {
   Serial.begin(9600);
   Serial.setTimeout(50);
   pinMode(sensorPin0, INPUT); 
   pinMode(sensorPin1, INPUT); 
   pinMode(sensorPin2, INPUT);
   pinMode(sensorPin3, INPUT); 
   pinMode(sensorPin4, INPUT); 
   pinMode(sensorPin5, INPUT);
   pinMode(lightpin1,OUTPUT);
   digitalWrite(lightpin1,LOW);
   pinMode(lightpin2,OUTPUT);
   digitalWrite(lightpin2,LOW);
   pinMode(lightpin3,OUTPUT);
   digitalWrite(lightpin3,LOW);
   pinMode(lightpin4,OUTPUT);
   digitalWrite(lightpin4,LOW);
   pinMode(lightpin5,OUTPUT);
   digitalWrite(lightpin5,LOW);
   pinMode(lightpin6,OUTPUT);
   digitalWrite(lightpin6,LOW);
   pinMode(lightpin7,OUTPUT);
   digitalWrite(lightpin7,LOW);
   pinMode(lightpin8,OUTPUT);
   digitalWrite(lightpin8,LOW);
   pinMode(lightpin9,OUTPUT);
   digitalWrite(lightpin9,LOW);
}
 
void loop(void) {
  inputstring=Serial.readStringUntil("\n");

//   outputstring1 = String("zero=");
//   outputstring1 = outputstring1+String(sensorValue0);
if (inputstring=="B\n") {
  outbool=true;
   sensorValue0 = analogRead(sensorPin0);
   sensorValue1 = analogRead(sensorPin1);
   sensorValue2 = analogRead(sensorPin2);
}
if (inputstring=="Q\n") {
  outbool2=true;
   sensorValue3 = analogRead(sensorPin3);
   sensorValue4 = analogRead(sensorPin4);
   sensorValue5 = analogRead(sensorPin5);
}
if (inputstring=="S\n") {outbool=false;}
if (inputstring=="lp1on\n") {digitalWrite(lightpin1,HIGH);}
if (inputstring=="lp1off\n") {digitalWrite(lightpin1,LOW);}
if (inputstring=="lp2on\n") {digitalWrite(lightpin2,HIGH);}
if (inputstring=="lp2off\n") {digitalWrite(lightpin2,LOW);}
if (inputstring=="lp3on\n") {digitalWrite(lightpin3,HIGH);}
if (inputstring=="lp3off\n") {digitalWrite(lightpin3,LOW);}
if (inputstring=="lp4on\n") {digitalWrite(lightpin4,HIGH);}
if (inputstring=="lp4off\n") {digitalWrite(lightpin4,LOW);}
if (inputstring=="lp5on\n") {digitalWrite(lightpin5,HIGH);}
if (inputstring=="lp5off\n") {digitalWrite(lightpin5,LOW);}
if (inputstring=="lp6on\n") {digitalWrite(lightpin6,HIGH);}
if (inputstring=="lp6off\n") {digitalWrite(lightpin6,LOW);}
if (inputstring=="lp7on\n") {digitalWrite(lightpin7,HIGH);}
if (inputstring=="lp7off\n") {digitalWrite(lightpin7,LOW);}
if (inputstring=="lp8on\n") {digitalWrite(lightpin8,HIGH);}
if (inputstring=="lp8off\n") {digitalWrite(lightpin8,LOW);}
if (inputstring=="lp9on\n") {digitalWrite(lightpin9,HIGH);}
if (inputstring=="lp9off\n") {digitalWrite(lightpin9,LOW);}
if (outbool) {
Serial.println(String(sensorValue0)+","+String(sensorValue1)+","+String(sensorValue2));
outbool=false;
}
if (outbool2) {
Serial.println(String(sensorValue3)+","+String(sensorValue4)+","+String(sensorValue5));
outbool2=false;
}
   //Wait(100)
   //Serial.println(sensorValue0);
   //Serial.println("one=");
   //Serial.println(sensorValue1);
   //Serial.println("two=");
   //Serial.println(sensorValue2);
}
