// Alıcı Kodu
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN pinleri
const byte address[6] = "00001";
unsigned long lastReceivedTime = 0;
const unsigned long timeout = 2000; // 20 ms zaman aşımı süresi
const int ppmPin = 2; // PPM çıkışı için D2 pini
const int ppmChannels = 5;
int ppmValues[ppmChannels];

struct DataPacket {
    int throttle;
    int yaw;
    int pitch;
    int roll;
    bool button;
};

void setup() {
    Serial.begin(9600);
    radio.begin();
    radio.openReadingPipe(0, address);
    radio.setPALevel(RF24_PA_MIN);
    radio.startListening();
    lastReceivedTime = millis();
    pinMode(ppmPin, OUTPUT);
}

void sendPPM() {
    noInterrupts();
    digitalWrite(ppmPin, HIGH);
    delayMicroseconds(300);
    digitalWrite(ppmPin, LOW);
    delayMicroseconds(300);
    for (int i = 0; i < ppmChannels; i++) {
        digitalWrite(ppmPin, HIGH);
        delayMicroseconds(ppmValues[i]);
        digitalWrite(ppmPin, LOW);
        delayMicroseconds(300);
    }
    interrupts();
}

void loop() {
    if (radio.available()) {
        DataPacket data;
        radio.read(&data, sizeof(data));
        lastReceivedTime = millis();
        
        ppmValues[0] = 0; 

        // 0-1023 aralığını 1000-2000 aralığına ölçekleme
        ppmValues[1] = map(data.roll, 150, 1000, 1000, 2000);  // Roll
        ppmValues[2] = map(data.pitch, 0, 1023, 1000, 2000);  // Pitch
        ppmValues[3] = map(data.throttle, 0, 1023, 1000, 2000);  // Throttle
        ppmValues[4] = map(data.yaw, 0, 1023, 1000, 2000);  // Yaw
        ppmValues[5] = 1000;
        if (data.button)
        {
          ppmValues[5] = 2000;
        }
        ppmValues[6] = 0;  // Radio6
        ppmValues[7] = 0;  // Radio7
        
        Serial.print("Alinan Veriler - Throttle: "); Serial.print(ppmValues[3]);
        Serial.print(" Yaw: "); Serial.print(ppmValues[4]);
        Serial.print(" Pitch: "); Serial.print(ppmValues[2]);
        Serial.print(" Roll: "); Serial.print(ppmValues[1]);
        Serial.print(" Button: "); Serial.println(ppmValues[5]);
    }
    
    sendPPM();
}