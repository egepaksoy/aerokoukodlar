// Verici Kodu
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN pinleri
const byte address[6] = "00001";

struct DataPacket {
    int throttle;
    int yaw;
    int pitch;
    int roll;
    int button;
};

void setup() {
    Serial.begin(9600);
    radio.begin();
    radio.openWritingPipe(address);
    radio.setPALevel(RF24_PA_MIN);
    radio.stopListening();
    pinMode(2, INPUT_PULLUP);
    pinMode(3, INPUT_PULLUP);
}

void loop() {
    DataPacket data;
    data.throttle = analogRead(A0);
    data.yaw = 1023 - analogRead(A1);  // Yaw değerini tersine çeviriyoruz
    data.pitch = analogRead(A3);
    data.roll = 1023 - analogRead(A4);  // Roll değerini tersine çeviriyoruz
    
    if (digitalRead(2) == LOW && digitalRead(3) == HIGH)
    {
      data.button = 0;
    }
    else if (digitalRead(2) == HIGH && digitalRead(3) == HIGH)
    {
      data.button = 1;
    }
    else if (digitalRead(2) == HIGH && digitalRead(3) == LOW)
    {
      data.button = 2;
    }

    bool success = radio.write(&data, sizeof(data));
    if (success)
    {
      Serial.print("Gonderilen Veriler - Throttle: "); Serial.print(data.throttle);
      Serial.print(" Yaw: "); Serial.print(data.yaw);
      Serial.print(" Pitch: "); Serial.print(data.pitch);
      Serial.print(" Roll: "); Serial.print(data.roll);
      Serial.print(" Button: "); Serial.println(data.button);
    }
    else
    {
      Serial.println("Hata");
    }
    
    delay(80);
}
