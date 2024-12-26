#include <Servo.h>

Servo myServoX; // Servo motor objesi
Servo myServoY; // Servo motor objesi

const int servoYPin = 9;      // Servo motor pini
const int servoXPin = 10;      // Servo motor pini
int artisMiktari = 2;

int joystickXValue = 500;
int joystickYValue = 500;

int currentXPosition = 90; // Servo başlangıç pozisyonu (orta)
int currentYPosition = 90; // Servo başlangıç pozisyonu (orta)

bool first = true;

void setup() {
  myServoX.attach(servoXPin);    // Servo motoru belirtilen pine bağla
  myServoX.write(currentXPosition); // Servo başlangıç pozisyonuna ayarla

  myServoY.attach(servoYPin);    // Servo motoru belirtilen pine bağla
  myServoY.write(currentYPosition); // Servo başlangıç pozisyonuna ayarla
  
  Serial.begin(9600);          // Seri iletişimi başlat
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
      if (joystickXValue > 900) {
        currentXPosition += artisMiktari;
        if (currentXPosition > 180) currentXPosition = 180;
        myServoX.write(currentXPosition);
      } else if (joystickXValue < 200) {
        currentXPosition -= artisMiktari;
        if (currentXPosition < 0) currentXPosition = 0;
        myServoX.write(currentXPosition);
      }

      if (joystickYValue > 900) {
        currentYPosition += artisMiktari;
        if (currentYPosition > 180) currentYPosition = 180;
        myServoY.write(currentYPosition);
      } else if (joystickYValue < 200) {
        currentYPosition -= artisMiktari;
        if (currentYPosition < 0) currentYPosition = 0;
        myServoY.write(currentYPosition);
      }

      Serial.println(joystickXValue);
      Serial.println(joystickYValue);

      delay(20);
    }
  }
}