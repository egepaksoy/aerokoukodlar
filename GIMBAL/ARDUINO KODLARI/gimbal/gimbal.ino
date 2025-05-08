#include <Servo.h>

Servo servoX;
Servo servoY;

int minX = 0;
int maxX = 180;

int minY = 90;
int maxY = 140;

int zeroX = 50;
int zeroY = 100;

int posX = zeroX;
int posY = zeroY;

int delayTime = 10;
int carpan = 2;

void setup() {
  Serial.begin(9600);
  servoX.attach(10);
  servoY.attach(9);

  servoX.write(posX);
  servoY.write(posY);
}


void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n'); // Satır sonuna kadar oku
    input.trim(); // Boşluk ve \r gibi karakterleri temizle

    int commaIndex = input.indexOf('|');
    if (commaIndex > 0) {
      String xStr = input.substring(0, commaIndex);
      String yStr = input.substring(commaIndex + 1);

      int x = xStr.toInt();
      int y = yStr.toInt();

      if (x == 2 || y == 2) {
        Serial.print(posX - zeroX);
        Serial.print("|");
        Serial.println(posY - zeroY);
      }

      else {
        // Geçerli servo açı aralığı değiştir
        if (posX + (x*carpan) > minX && posX + (x*carpan) < maxX) {
          posX += (x * carpan);
        }
        if (posY + (y*carpan) > minY && posY + (y*carpan) < maxY) {
          posY += (y * carpan);
        }
        servoX.write(posX);
        servoY.write(posY);
        delay(delayTime);
      }
    }
  }
}