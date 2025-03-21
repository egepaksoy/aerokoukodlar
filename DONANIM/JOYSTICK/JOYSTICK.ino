#define JOYSTICK_X A0
#define JOYSTICK_Y A1
#define BUTTON_PIN 9  // Butonun bağlı olduğu pin

void setup() {
  // Seri haberleşmeyi başlat
  Serial.begin(9600);

  // Buton pinini giriş olarak ayarla
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Buton bağlı olduğunda LOW olacak şekilde
}

void loop() {
  // Joystick değerlerini oku
  int joystickXValue = analogRead(JOYSTICK_X);
  int joystickYValue = analogRead(JOYSTICK_Y);

  // Buton durumu oku (düğme basılı mı)
  int buttonState = digitalRead(BUTTON_PIN);

  // Buton basılı değilse
  if (buttonState == HIGH) {
    // Joystick değerlerini seri monitöre yazdır
    Serial.print(joystickXValue);
    Serial.print("|");
    Serial.println(joystickYValue);
  } else {
    // Butona basıldığında farklı bir şey yazdır
    Serial.println("0|0|0");
  }

  // Gecikme
  delay(15);
}
