#include <Servo.h>

Servo myServoX; // Servo motor objesi
Servo myServoY; // Servo motor objesi
const int joystickXPin = A2; // Joystick'in X ekseni pini
const int joystickYPin = A3; // Joystick'in X ekseni pini
const int servoYPin = 9;      // Servo motor pini
const int servoXPin = 10;      // Servo motor pini
int artisMiktari = 2;

int currentXPosition = 90; // Servo başlangıç pozisyonu (orta)
int currentYPosition = 90; // Servo başlangıç pozisyonu (orta)

void setup() {
  myServoX.attach(servoXPin);    // Servo motoru belirtilen pine bağla
  myServoX.write(currentXPosition); // Servo başlangıç pozisyonuna ayarla

  myServoY.attach(servoYPin);    // Servo motoru belirtilen pine bağla
  myServoY.write(currentYPosition); // Servo başlangıç pozisyonuna ayarla
  
  Serial.begin(9600);          // Seri iletişimi başlat
}

void loop() {
  int joystickXValue = analogRead(joystickXPin); // Joystick X eksen değerini oku
  int joystickYValue = analogRead(joystickYPin); // Joystick X eksen değerini oku
  Serial.println(joystickYValue);               // Değeri seri monitörde görüntüle
  Serial.println(joystickXValue);               // Değeri seri monitörde görüntüle

  // Joystick sağa hareket ettirildiğinde (orta pozisyonun dışında)
  if (joystickXValue > 900) {
    currentXPosition += artisMiktari; // Servo pozisyonunu artır
    if (currentXPosition > 180) currentXPosition = 180; // Maksimum 180 dereceyi sınırla
    myServoX.write(currentXPosition); // Servo yeni pozisyona döner
  } 
  // Joystick sola hareket ettirildiğinde
  else if (joystickXValue < 200) {
    currentXPosition -= artisMiktari; // Servo pozisyonunu azalt
    if (currentXPosition < 0) currentXPosition = 0; // Minimum 0 dereceyi sınırla
    myServoX.write(currentXPosition); // Servo yeni pozisyona döner
  }

  // Joystick sağa hareket ettirildiğinde (orta pozisyonun dışında)
  if (joystickYValue > 900) {
    currentYPosition += artisMiktari; // Servo pozisyonunu artır
    if (currentYPosition > 180) currentYPosition = 180; // Maksimum 180 dereceyi sınırla
    myServoY.write(currentYPosition); // Servo yeni pozisyona döner
  } 
  // Joystick sola hareket ettirildiğinde
  else if (joystickYValue < 200) {
    currentYPosition -= artisMiktari; // Servo pozisyonunu azalt
    if (currentYPosition < 0) currentYPosition = 0; // Minimum 0 dereceyi sınırla
    myServoY.write(currentYPosition); // Servo yeni pozisyona döner
  }

  delay(15); // Servo hareketini stabilize etmek için bekleme süresi
}
