#include <Servo.h>

// Servo nesneleri
Servo servoX;
Servo servoY;

// Joystick pin tanımlamaları
#define JOYSTICK_X A0 // X ekseni
#define JOYSTICK_Y A1 // Y ekseni

// Servo pin tanımlamaları
#define SERVO_X_PIN 9  // X ekseni servosu
#define SERVO_Y_PIN 10 // Y ekseni servosu

// Servo sınırları
const int ANGLE_MIN = 0;
const int ANGLE_MAX = 180;

void setup() {
  // Servo bağlantıları
  servoX.attach(SERVO_X_PIN);
  servoY.attach(SERVO_Y_PIN);

  // Servoları başlangıç pozisyonuna ayarla
  servoX.write(90);
  servoY.write(90);

  // Seri haberleşmeyi başlat
  Serial.begin(9600);
}

void loop() {
  // Joystick değerlerini oku
  int joystickXValue = analogRead(JOYSTICK_X);
  int joystickYValue = analogRead(JOYSTICK_Y);

  // X ve Y değerlerini servo açılarına dönüştür
  int angleX = map(joystickXValue, 0, 1023, ANGLE_MIN, ANGLE_MAX);
  int angleY = map(joystickYValue, 0, 1023, ANGLE_MIN, ANGLE_MAX);

  // Servo motorlara açı gönder
  servoX.write(angleX);
  servoY.write(angleY);

  // Debug verileri seri monitöre yazdır
  Serial.print("Joystick X: ");
  Serial.print(joystickXValue);
  Serial.print(" -> Servo X: ");
  Serial.print(angleX);
  Serial.print(" | Joystick Y: ");
  Serial.print(joystickYValue);
  Serial.print(" -> Servo Y: ");
  Serial.println(angleY);

  // Gecikme
  delay(15);
}