#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10);  // CE, CSN pinleri
const byte address[6] = "00001";
int joystickData[3];

void setup() {
  Serial.begin(9600);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(2, INPUT_PULLUP);

  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.stopListening();
}

void loop() {
  joystickData[0] = analogRead(A0); // X ekseni
  joystickData[1] = analogRead(A1); // Y ekseni
  joystickData[2] = digitalRead(2); // Buton durumu

  Serial.print("X: ");
  Serial.print(joystickData[0]);
  Serial.print(" | Y: ");
  Serial.print(joystickData[1]);
  Serial.print(" | Button: ");
  Serial.println(joystickData[2]);

  bool ok = radio.write(&joystickData, sizeof(joystickData));

  if (ok) {
    Serial.println("Data sent successfully");
  } else {
    Serial.println("Failed to send data");
  }

  delay(50);
}
