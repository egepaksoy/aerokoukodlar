#define JOYSTICK_X A0
#define JOYSTICK_Y A1

void setup() {
  // Seri haberleşmeyi başlat
  Serial.begin(9600);
}

void loop() {
  // Joystick değerlerini oku
  int joystickXValue = analogRead(JOYSTICK_X);
  int joystickYValue = analogRead(JOYSTICK_Y);

  // Debug verileri seri monitöre yazdır
  // Serial.print("Joystick X: ");
  Serial.print(joystickXValue);
  Serial.print("|");
  // Serial.print(" | Joystick Y: ");
  Serial.println(joystickYValue);

  // Gecikme
  delay(15);
}