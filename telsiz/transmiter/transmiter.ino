#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

RF24 radio(7, 8); // CE, CSN pinleri

const byte address[6] = "00001"; // Haberleşme adresi
int message = 1; // Gönderilecek veri

void setup() {
  radio.begin();
  radio.openWritingPipe(address); // Verici adresi
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
}

void loop() {
  // Mesaj gönder
  radio.write(&message, sizeof(message));
  delay(100); // 100 ms aralıkla mesaj gönder
}
