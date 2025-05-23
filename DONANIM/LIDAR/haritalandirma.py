import smbus
import time
import cv2
import numpy as np

# I2C adresi ve registerlar
LIDAR_ADDR = 0x62
ACQ_COMMAND = 0x00
FULL_DELAY_HIGH = 0x0f

# I2C başlat
bus = smbus.SMBus(1)  # Raspberry Pi için genelde 1 numaralı I2C

# Mesafe okuma fonksiyonu
def read_distance():
    try:
        bus.write_byte_data(LIDAR_ADDR, ACQ_COMMAND, 0x04)
        time.sleep(0.02)
        high = bus.read_byte_data(LIDAR_ADDR, FULL_DELAY_HIGH)
        low = bus.read_byte_data(LIDAR_ADDR, FULL_DELAY_HIGH + 1)
        return (high << 8) + low
    except:
        return -1

# OpenCV penceresini başta oluştur
cv2.namedWindow("LIDAR Görselleştirme", cv2.WINDOW_AUTOSIZE)

try:
    while True:
        distance = read_distance()

        if distance == -1:
            print("Mesafe okuma hatası")
            continue

        print("Mesafe:", distance, "mm")

        # 0-4000 mm arası normalize
        norm = min(max(distance, 0), 4000) / 4000.0
        color_val = int(norm * 255)
        color = (255 - color_val, 0, color_val)  # Mavi → Kırmızı

        # Görsel oluştur
        frame = np.full((300, 300, 3), color, dtype=np.uint8)
        cv2.putText(frame, f"{distance} mm", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        # Tek pencereyi güncelle
        cv2.imshow("LIDAR Görselleştirme", frame)

        # Çıkmak için q tuşu
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Klavye ile durduruldu.")

finally:
    cv2.destroyAllWindows()
