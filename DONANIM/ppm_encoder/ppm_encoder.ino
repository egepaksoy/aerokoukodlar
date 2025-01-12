const int ppmPin = 12;  // PPM çıkış pini
const int channelCount = 8;  // PPM kanal sayısı
int channels[channelCount] = {1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500};  // PWM değerleri (1000-2000 µs)

// PPM sinyali için sabitler
const int PPM_SYNC = 300;  // Sync süresi (ms)
const int PPM_FRAME_LENGTH = 22500;  // PPM frame uzunluğu (ms)

void setup() {
    Serial.begin(9600);  // Serial iletişim başlat
    pinMode(ppmPin, OUTPUT);
    digitalWrite(ppmPin, LOW);
    Serial.println("PPM Receiver Started. Send PWM values as: 1000 1500 1200 2000...");
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');  // Satır sonuna kadar veri oku
        parseInput(input);
        Serial.println(input);
    }
    sendPPM();  // PPM sinyalini gönder
}

void parseInput(String input) {
    int index = 0;
    char *ptr = strtok((char *)input.c_str(), " ");  // Boşluklara göre parçala

    while (ptr != NULL && index < channelCount) {
        int value = atoi(ptr);  // String'i integer'a çevir
        if (value >= 1000 && value <= 2000) {  // Geçerli PWM kontrolü
            channels[index] = value;
        } else {
            channels[index] = 1500;  // Hatalı değer gelirse default değer
        }
        Serial.println(channels[index]);
        index++;
        ptr = strtok(NULL, " ");
    }
}

void sendPPM() {
    unsigned long startTime = micros();
    digitalWrite(ppmPin, HIGH);
    delayMicroseconds(PPM_SYNC);  // Sync sinyali gönder

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
