int analogPin = A0;  // Analog veri okunacak pin
int analogValue = 0; // Okunan değeri saklamak için değişken

void setup() {
  Serial.begin(115200);  // Seri iletişim başlat (9600 baud rate)
  Serial.println("Analog Porttan Değer Okuma Başlıyor...");

}

void loop() {
  analogValue = analogRead(analogPin);  // Analog pinden veri oku
  Serial.print("Okunan Analog Deger: ");
  Serial.println(analogValue);  // Okunan değeri seri monitöre yazdır
  delay(500);  // Yarım saniye bekle (okuma hızını kontrol etmek için)
}
