const float mvc = 4.2;
float counts = 0;
float mv = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  counts = analogRead(A1);
  Serial.print("Counts: ");
  Serial.println(counts); // String kullanmadan doğrudan yazdır
  mv = counts * mvc;
  Serial.print("Volt: ");
  Serial.println(mv); // String kullanmadan doğrudan yazdır
  delay(1000);
}
