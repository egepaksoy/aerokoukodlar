#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

RF24 radio(7, 8); // CE, CSN pinleri
const byte address[6] = "00001"; // Haberleşme adresi

int ledPin = 2; // LED pin numarası
int message = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  radio.begin();
  radio.openReadingPipe(0, address); // Alıcı adresi
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.startListening(); // Alıcıyı başlat
}

void loop() {
  if (radio.available()) {
    radio.read(&message, sizeof(message)); // Gelen mesajı oku

    // Sinyal geldiyse LED'i yakıp söndür
    if (message == 1) {
      
      digitalWrite(LED_BUILTIN, HIGH);
      delay(1000);
      digitalWrite(LED_BUILTIN, LOW);
      delay(1000);
    }
  } else {
    // Sinyal yoksa LED'i kapalı tut
    digitalWrite(LED_BUILTIN, LOW);
  }
}
