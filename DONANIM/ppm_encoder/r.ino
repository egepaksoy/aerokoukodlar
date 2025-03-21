#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10);
const byte address[6] = "00001";

const int ppmPin = 9;
const int channelCount = 8;
int channels[channelCount] = {1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500};

const int PPM_SYNC = 300;
const int PPM_FRAME_LENGTH = 22500;

int joystickData[3];
int xAxis, yAxis, buttonState;

void setup() {
  Serial.begin(9600);
  pinMode(ppmPin, OUTPUT);
  digitalWrite(ppmPin, LOW);

  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.startListening();
}

void loop() {
  if (radio.available()) {
    radio.read(&joystickData, sizeof(joystickData));

    xAxis = map(joystickData[0], 0, 1023, 1000, 2000);
    yAxis = map(joystickData[1], 0, 1023, 1000, 2000);
    buttonState = joystickData[2];

    Serial.print("X: ");
    Serial.print(xAxis);
    Serial.print(" | Y: ");
    Serial.print(yAxis);
    Serial.print(" | Button: ");
    Serial.println(buttonState);

    channels[0] = xAxis;
    channels[1] = yAxis;
    channels[2] = buttonState == 1 ? 2000 : 1000;
  }

  sendPPM();
}

void sendPPM() {
  unsigned long startTime = micros();
  
  digitalWrite(ppmPin, HIGH);
  delayMicroseconds(PPM_SYNC);
  
  for (int i = 0; i < channelCount; i++) {
    digitalWrite(ppmPin, LOW);
    delayMicroseconds(channels[i]);
    digitalWrite(ppmPin, HIGH);
    delayMicroseconds(300);
  }

  while (micros() - startTime < PPM_FRAME_LENGTH) {
    delayMicroseconds(100);
  }
}
