#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10);
const byte address[6] = "00001";

// PPM çıkış pini ve kanal sayısı
const int ppmPin = 9;
const int channelCount = 8;
int channels[channelCount] = {1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500};  // PWM değerleri (1000-2000 µs)

// PPM sinyali için sabitler
const int PPM_SYNC = 300;  // Sync süresi (ms)
const int PPM_FRAME_LENGTH = 22500;  // PPM frame uzunluğu (ms)

// Datalar
int joystickData[3];
int xAxis, yAxis, buttonState;

void setup() {
  Serial.begin(9600);
  
  // Bağlantılar
  pinMode(A0, INPUT); // Joystick X ekseni
  pinMode(A1, INPUT); // Joystick Y ekseni
  pinMode(2, INPUT_PULLUP); // Buton
  
  radio.begin();
  if (!radio.begin()) {
    Serial.println("NRF modülü başlatılamadı!");
    while (1);
  }

  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.startListening();

  Serial.println("Radi başlatıldı")

  pinMode(ppmPin, OUTPUT);
  digitalWrite(ppmPin, LOW);
}

void loop() {
  if (radio.available()) {
    radio.read(&joystickData, sizeof(joystickData));
    xAxis = map(joystickData[0], 0, 1023, 1000, 2000);  // X eksenini 1000-2000
    yAxis = map(joystickData[1], 0, 1023, 1000, 2000);  // Y eksenini 1000-2000
    buttonState = joystickData[2];

    Serial.print("X: ");
    Serial.print(xAxis);
    Serial.print(" | Y: ");
    Serial.print(yAxis);
    Serial.print(" | Button: ");
    Serial.println(buttonState);
  }
  
  channels[0] = xAxis;  // X ekseni PWM değeri
  channels[1] = yAxis;  // Y ekseni PWM değeri
  channels[2] = buttonState == 1 ? 2000 : 1000;

  sendPPM();  // PPM sinyalini gönder
}

void sendPPM() {
  unsigned long startTime = micros();
  
  // Sync sinyali gönder
  digitalWrite(ppmPin, HIGH);
  delayMicroseconds(PPM_SYNC);
  
  for (int i = 0; i < channelCount; i++) {
    digitalWrite(ppmPin, LOW);
    delayMicroseconds(channels[i]);  // Kanal değeri kadar LOW sinyal
    digitalWrite(ppmPin, HIGH);
    delayMicroseconds(300);  // Sabit süre (PPM standardı)
  }

  // Frame'in kalan süresi için bekle
  while (micros() - startTime < PPM_FRAME_LENGTH) {
    delayMicroseconds(100);
  }
}