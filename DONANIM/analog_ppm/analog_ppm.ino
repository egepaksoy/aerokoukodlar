const int ppmPin = 9;  // PPM çıkış pini
const int channelCount = 8;  // Toplam kanal sayısı
int channels[channelCount] = {1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500};  // Varsayılan PWM değerleri (1000-2000 µs)

const int syncLength = 300;  // Sync sinyal süresi (300 µs)
const int frameLength = 22500;  // PPM çerçeve süresi (22500 µs)

void setup() {
    pinMode(ppmPin, OUTPUT);  // PPM pini çıkış olarak ayarla
    digitalWrite(ppmPin, LOW);
}

void loop() {
    // Analog pinlerden veri oku ve PPM kanallarına ata
    channels[0] = map(analogRead(A0), 0, 1023, 1000, 2000);  // Kanal 1
    channels[1] = map(analogRead(A1), 0, 1023, 1000, 2000);  // Kanal 2
    channels[2] = map(analogRead(A2), 0, 1023, 1000, 2000);  // Kanal 3
    channels[3] = map(analogRead(A3), 0, 1023, 1000, 2000);  // Kanal 4
    channels[4] = 1500;  // Sabit değerli kanal örneği
    channels[5] = 1500;
    channels[6] = 1500;
    channels[7] = 1500;

    sendPPMSignal();  // PPM sinyalini gönder
    delay(20);  // 20 ms gecikme (PPM frekansı yaklaşık 50 Hz)
}

void sendPPMSignal() {
    unsigned long startTime = micros();  // Çerçevenin başlangıç zamanını kaydet

    // Sync sinyali gönder
    digitalWrite(ppmPin, HIGH);
    delayMicroseconds(syncLength);
    digitalWrite(ppmPin, LOW);

    // Her bir kanal değerini gönder
    for (int i = 0; i < channelCount; i++) {
        delayMicroseconds(channels[i]);  // Kanal süresi boyunca LOW sinyali
        digitalWrite(ppmPin, HIGH);
        delayMicroseconds(300);  // 300 µs LOW-HIGH geçiş süresi
        digitalWrite(ppmPin, LOW);
    }

    // Kalan frame süresini doldur
    while (micros() - startTime < frameLength) {
        delayMicroseconds(100);  // Döngü yükünü azaltmak için kısa gecikme
    }
}
