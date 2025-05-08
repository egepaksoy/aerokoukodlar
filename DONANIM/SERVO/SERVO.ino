#include <Servo.h>

Servo myServoX; // Servo motor objesi
Servo myServoY; // Servo motor objesi

const int servoYPin = 9;      // Servo motor Y pini
const int servoXPin = 10;      // Servo motor X pini

int artisMiktari = 2;

int joystickXValue = 500;
int joystickYValue = 500;

const int startXPosition = 90; // Servo başlangıç pozisyonu (orta)
const int startYPosition = 140; // Servo başlangıç pozisyonu (orta)

const int maxYAngle = 140;
const int minYAngle = 90;

const int maxXAngle = 170;
const int minXAngle = 10;

const int zeroAngleY = 110;
const int zeroAngleX = 90;

int calcAngleX;
int calcAngleY;

int currentXPosition;
int currentYPosition;

void setup() {
  myServoX.attach(servoXPin);
  myServoX.write(startXPosition); // Servo başlangıç pozisyonuna ayarla

  myServoY.attach(servoYPin);
  myServoY.write(startYPosition); // Servo başlangıç pozisyonuna ayarla
  
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String receivedData = Serial.readStringUntil('\n');
    
    if (receivedData.indexOf("|") < 0) {
      joystickXValue = 500;
      joystickYValue = 500;
    }

    joystickXValue = receivedData.substring(0, receivedData.indexOf("|")).toInt();
    joystickYValue = receivedData.substring(receivedData.indexOf("|") + 1).toInt();

    while (Serial.available() <= 0) {
      if (joystickXValue > 900 && currentXPosition < maxXAngle) {
        currentXPosition += artisMiktari;
        if (currentXPosition > 180) currentXPosition = 180;
        myServoX.write(currentXPosition);
      } else if (joystickXValue < 200 && currentXPosition > minXAngle) {
        currentXPosition -= artisMiktari;
        if (currentXPosition < 0) currentXPosition = 0;
        myServoX.write(currentXPosition);
      }

      if (joystickYValue > 900 && currentYPosition < maxYAngle) {
        currentYPosition += artisMiktari;
        if (currentYPosition > 180) currentYPosition = 180;
        myServoY.write(currentYPosition);
      } else if (joystickYValue < 200 && currentYPosition > minYAngle) {
        currentYPosition -= artisMiktari;
        if (currentYPosition < 0) currentYPosition = 0;
        myServoY.write(currentYPosition);
      }

      calcAngleY = abs(currentYPosition - zeroAngleY);
      calcAngleX = (zeroAngleX - currentXPosition) * -1;

      Serial.print(calcAngleX);
      Serial.print("|");
      Serial.println(calcAngleY);

      delay(20);
    }
  }
}