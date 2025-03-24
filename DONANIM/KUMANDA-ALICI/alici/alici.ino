// Alıcı Kodu
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN pinleri
const byte address[6] = "00001";
unsigned long lastReceivedTime = 0;
const unsigned long timeout = 2000; // 20 ms zaman aşımı süresi
const int ppmPin = 2; // PPM çıkışı için D2 pini
const int ppmChannels = 8;
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
    static unsigned long lastPPMTime = 0; // Son gönderilen PPM sinyalinin zamanı
    const unsigned int syncPulse = 5000; // 5ms Sync darbesi
    const unsigned int gapTime = 300;    // Kanal arası boşluk süresi (300µs)
    
    noInterrupts(); // Kesintileri devre dışı bırak

    unsigned long startTime = micros(); // PPM sinyalinin başlangıç zamanı

    // Sync Pulse - Çerçevenin başlangıcını belirtir
    digitalWrite(ppmPin, HIGH);
    delayMicroseconds(300);
    digitalWrite(ppmPin, LOW);
    delayMicroseconds(syncPulse);

    for (int i = 0; i < ppmChannels; i++) {
        digitalWrite(ppmPin, HIGH);
        delayMicroseconds(ppmValues[i] - 300);  // Kanalın süresi (-300 mission planner'da ayarlamak için)
        digitalWrite(ppmPin, LOW);
        delayMicroseconds(gapTime);  // Kanal arası boşluk
    }

    interrupts(); // Kesintileri tekrar aç

    // Çerçevenin tamamlanma süresini kontrol et
    unsigned long elapsedTime = micros() - startTime;
    unsigned long frameTime = 22000; // 22ms toplam çerçeve süresi (50Hz)

    if (elapsedTime < frameTime) {
        delayMicroseconds(frameTime - elapsedTime); // PPM çerçevesini tamamla
    }
}


void loop() {
    if (radio.available()) {
        DataPacket data;
        radio.read(&data, sizeof(data));
        lastReceivedTime = millis();
        
        ppmValues[0] = 0; 

        // 0-1023 aralığını 1000-2000 aralığına ölçekleme
        ppmValues[1] = map(data.roll, 60, 820, 1200, 1800);  // Roll
        ppmValues[2] = map(data.pitch, 150, 785, 1200, 1800);  // Pitch
        ppmValues[3] = map(data.throttle, 204, 850, 1200, 1800);  // Throttle
        ppmValues[4] = map(data.yaw, 195, 930, 1200, 1800);  // Yaw
        ppmValues[5] = 1100 + data.button * 280;
        ppmValues[6] = 1100;  // Radio6
        ppmValues[7] = 1100;  // Radio7
        
        // Serial.print("Alinan Veriler - Throttle: "); Serial.print(ppmValues[3]);
        // Serial.print(" Yaw: "); Serial.print(ppmValues[4]);
        // Serial.print(" Pitch: "); Serial.print(ppmValues[2]);
        // Serial.print(" Roll: "); Serial.print(ppmValues[1]);
        // Serial.print(" Button: "); Serial.println(ppmValues[5]);

        Serial.print("Alinan Veriler - Throttle: "); Serial.print(data.throttle);
        Serial.print(" Yaw: "); Serial.print(data.yaw);
        Serial.print(" Pitch: "); Serial.print(data.pitch);
        Serial.print(" Roll: "); Serial.print(data.roll);
        Serial.print(" Button: "); Serial.println(data.button);
    }
    
    sendPPM();
}