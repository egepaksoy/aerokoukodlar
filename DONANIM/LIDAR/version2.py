import smbus
import time

# LIDAR Lite v3'ün I2C adresi
LIDAR_ADDRESS = 0x62
bus = smbus.SMBus(1)  # Raspberry Pi'de I2C-1 hattı kullanılıyor

def read_lidar(repeat=5):
    """ 
    LIDAR Lite v3'ten mesafe okur, birkaç ölçüm alarak ortalama hesaplar.
    repeat: Ortalama alınacak ölçüm sayısı (Gürültüyü azaltır).
    """
    distances = []
    
    for _ in range(repeat):
        try:
            # LIDAR'a ölçüm yapmasını söyle
            bus.write_byte_data(LIDAR_ADDRESS, 0x00, 0x04)
            time.sleep(0.02)  # Ölçüm süresi

            # 16-bit mesafe verisini oku
            high_byte = bus.read_byte_data(LIDAR_ADDRESS, 0x0f)
            low_byte = bus.read_byte_data(LIDAR_ADDRESS, 0x10)
            distance_cm = (high_byte << 8) + low_byte  # Mesafeyi cm olarak hesapla

            if 0 < distance_cm < 4000:  # LIDAR'ın ölçebileceği mesafe aralığı
                distances.append(distance_cm)
            else:
                print("Geçersiz ölçüm alındı, tekrar deneniyor...")
            
        except OSError:
            print("I2C bağlantı hatası! LIDAR bağlı mı?")
            return None  # Bağlantı hatası olursa None döndür

        time.sleep(0.01)  # Sensörün stabilize olması için bekleme süresi
    
    if not distances:
        return None  # Geçerli ölçüm alınamadıysa None döndür

    avg_distance_cm = sum(distances) / len(distances)  # Ölçümleri ortalama alarak hassasiyeti artır
    avg_distance_m = avg_distance_cm / 100  # Metreye çevir

    return round(avg_distance_m, 3)  # Ölçümü metre cinsinden 3 ondalık basamakla döndür

try:
    while True:
        mesafe_m = read_lidar()
        if mesafe_m is not None:
            print(f"Mesafe: {mesafe_m} m")
        else:
            print("Ölçüm başarısız!")
        
        time.sleep(1)  # 1 saniye aralıklarla ölçüm yap
except KeyboardInterrupt:
    print("\nLIDAR durduruldu.")
