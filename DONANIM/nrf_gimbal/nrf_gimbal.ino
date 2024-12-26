#include <Servo.h>

// Servo motor nesneleri
Servo servo1;
Servo servo2;

// Servo pinleri
const int servo1Pin = 9; // Servo 1 için PWM pini
const int servo2Pin = 10; // Servo 2 için PWM pini

void setup() {
  Serial.begin(9600); // Seri haberleşme için baud rate
  servo1.attach(servo1Pin); // Servo 1'i bağla
  servo2.attach(servo2Pin); // Servo 2'yi bağla

  // Başlangıç açıları
  servo1.write(90);
  servo2.write(90);
  Serial.println("Servo kontrol başlatıldı.");
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n'); // '\n' karakterine kadar olan veriyi oku

    // Gelen veriyi kontrol et
    if (data.length() > 0) {
      Serial.print("Gelen veri: ");
      Serial.println(data);

      // Veriyi parçala
      int sepIndex = data.indexOf('|');
      if (sepIndex != -1) {
        String servo1Data = data.substring(0, sepIndex); // İlk servo için veri
        String servo2Data = data.substring(sepIndex + 1); // İkinci servo için veri

        // Servo 1 verisini ayrıştır
        int angle1 = servo1Data.toInt();
        int angle2 = servo2Data.toInt();
        if (angle1 >= 0 && angle1 <= 180 && angle2 >= 0 && angle2 <= 180) {
          servo1.write(angle1);
          servo2.write(angle2);
          Serial.print("Servo 1 açısı: ");
          Serial.print(angle1);
          Serial.print("Servo 2 açısı: ");
          Serial.println(angle2);
        }

      } else {
        Serial.println("Geçersiz veri formatı!");
      }
    }
  }
}
