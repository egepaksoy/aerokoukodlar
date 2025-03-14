import smbus
import time

# LIDAR Lite v3'ün I2C adresi
LIDAR_ADDRESS = 0x62
bus = smbus.SMBus(1)  # Raspberry Pi'de I2C-1 hattını kullan

def read_lidar():
    """ LIDAR Lite v3'ten mesafe okuma """
    bus.write_byte_data(LIDAR_ADDRESS, 0x00, 0x04)  # Ölçüm başlat
    time.sleep(0.02)  # Ölçüm tamamlanmasını bekle

    high_byte = bus.read_byte_data(LIDAR_ADDRESS, 0x0f)  # Üst 8 bit
    low_byte = bus.read_byte_data(LIDAR_ADDRESS, 0x10)   # Alt 8 bit

    distance = (high_byte << 8) + low_byte  # 16 bitlik mesafe değeri
    return distance

try:
    while True:
        mesafe = read_lidar()
        print(f"Mesafe: {mesafe} cm")
        time.sleep(1)  # 1 saniye bekle

except KeyboardInterrupt:
    print("\nLIDAR durduruldu.")