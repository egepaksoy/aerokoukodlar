#include <Servo.h>

Servo servoX;
Servo servoY;

const int servoXPin = 9;
const int servoYPin = 10;

const int servoXAnalogPin = A0;
const int servoYAnalogPin = A1;

int hassasiyet = 2;

int currentXPosition = 90;
int currentYPosition = 90;

int xValue = -1;
int yValue = -1;

void setup() {
  servoX.attach(servoXPin);
  servoY.attach(servoYPin);
  
  servoX.write(currentXPosition);
  servoY.write(currentYPosition);

  Serial.begin(9600);
}

void loop() {
  String data = Serial.readStringUntil("\n");
  int delimeterIndex = data.indexOf("|");

  Serial.println(xValue);
  Serial.println(yValue);

  if (delimeterIndex != -1) {
    xValue = data.substring(0, delimeterIndex).toInt();
    yValue = data.substring(delimeterIndex + 1).toInt();
  }

  if (xValue != -1) {
    if (xValue > 900) {
      currentXPosition += hassasiyet;
      
      if (currentXPosition > 180) currentXPosition = 180;
      servoX.write(currentXPosition);
    }

    else if (xValue < 200) {
      currentXPosition -= hassasiyet; // Servo pozisyonunu azalt
      if (currentXPosition < 0) currentXPosition = 0; // Minimum 0 dereceyi sınırla
      servoX.write(currentXPosition); // Servo yeni pozisyona döner
    }
  }

  if (yValue != -1) {
    if (yValue > 900) {
      currentYPosition += hassasiyet;
      
      if (currentYPosition > 180) currentYPosition = 180;
      servoY.write(currentYPosition);
    }

    else if (yValue < 200) {
      currentYPosition -= hassasiyet; // Servo pozisyonunu azalt
      if (currentYPosition < 0) currentYPosition = 0; // Minimum 0 dereceyi sınırla
      servoY.write(currentYPosition); // Servo yeni pozisyona döner
    }
  }

  delay(15);
}