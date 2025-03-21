#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10);
const byte address[6] = "00001";

int xAxis, yAxis, buttonState;

void setup() {
  Serial.begin(9600);

  pinMode(A0, INPUT); // X ekseni
  pinMode(A1, INPUT); // Y ekseni
  pinMode(2, INPUT_PULLUP); // Buton
  
  radio.begin();
  if (!radio.begin()) {
    Serial.println("NRF modülü başlatılamadı!");
    while (1);
  }
  
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.stopListening();
}

void loop() {
  xAxis = analogRead(A0);
  yAxis = analogRead(A1);
  buttonState = !digitalRead(2); // Düğmeye basıldığında LOW yerine HIGH döner

  Serial.print("X: ");
  Serial.print(xAxis);
  Serial.print(" | Y: ");
  Serial.print(yAxis);
  Serial.print(" | Button: ");
  Serial.println(buttonState);

  int joystickData[3] = {xAxis, yAxis, buttonState};

  bool success = radio.write(&joystickData, sizeof(joystickData));
  if (success) {
      Serial.println("Veri başarıyla gönderildi");
  } else {
      Serial.println("Veri gönderilemedi!");
  }

  delay(100);
}