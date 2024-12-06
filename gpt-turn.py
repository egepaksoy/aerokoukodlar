from pymavlink import mavutil
import time

def send_yaw_rate(master, yaw_rate, duration):
    """
    Saat yönünde dronu döndürecek komutları gönderir.
    :param master: MAVLink bağlantı nesnesi
    :param yaw_rate: Dönüş hızı (derece/saniye)
    :param duration: Dönüş süresi (saniye)
    """
    start_time = time.time()
    while time.time() - start_time < duration:
        # Dronun bulunduğu yerde yaw hızını ayarla
        master.mav.set_position_target_local_ned_send(
            0,  # time_boot_ms (otomatik doldurulacak)
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000011111000111,  # Sadece yaw hızını kontrol et
            0, 0, 0,  # Konum ayarlanmıyor
            0, 0, 0,  # Hız ayarlanmıyor
            0, 0, yaw_rate,  # Yaw hızını belirle
            0, 0  # Akselerasyon ayarlanmıyor
        )
        time.sleep(0.1)


def main():
    # MAVLink bağlantısını başlat
    master = mavutil.mavlink_connection('udp:172.22.160.1:14550')  # Bağlantı türünü ayarla (örneğin: seri, UDP, vb.)
    
    # Bağlantının kurulduğunu doğrula
    master.wait_heartbeat()
    print("Drone ile bağlantı kuruldu!")

    # GUIDED moda geç
    master.set_mode('GUIDED')

    # Arm işlemi
    master.arducopter_arm()
    print("Drone ARM edildi!")

    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 5)
    time.sleep(10)
    print("takeoff basarılı")


    # Saat yönünde dön (yaw_rate pozitif: saat yönü, negatif: saat tersi)
    yaw_rate = 30  # Dönüş hızı (derece/saniye)
    duration = 10  # Dönüş süresi (saniye)
    send_yaw_rate(master, yaw_rate, duration)

    # İşlem sonrası disarm işlemi (isteğe bağlı)
    master.arducopter_disarm()
    print("Drone DISARM edildi!")

if __name__ == "__main__":
    main()
