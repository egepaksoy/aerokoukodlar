import time
import sys
import threading
from picamera2 import Picamera2
import cv2
import numpy as np
import struct
import socket
import queue
from math import ceil

sys.path.append('./pymavlink_custom')
from pymavlink_custom import Vehicle
from mqtt_controller import magnet_control, rotate_servo, cleanup


def failsafe(vehicle):
    def failsafe_drone_id(vehicle, drone_id):
        print(f"{drone_id}>> Failsafe alıyor")
        vehicle.set_mode(mode="RTL", drone_id=drone_id)
    threads = []
    for d_id in vehicle.drone_ids:
        t = threading.Thread(target=failsafe_drone_id, args=(vehicle, d_id))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(f"Dronlar {vehicle.drone_ids} Failsafe aldı")

def is_equilateral(approx, tolerance=0.15):
    if len(approx) < 3:
        return False
    sides = []
    for i in range(len(approx)):
        pt1 = approx[i][0]
        pt2 = approx[(i + 1) % len(approx)][0]
        dist = np.linalg.norm(pt1 - pt2)
        sides.append(dist)
    mean = np.mean(sides)
    return all(abs(s - mean) / mean < tolerance for s in sides)

def image_recog_new(picam2, ip: str, port: int, stop_event: threading.Event, broadcast_started: threading.Event, shared_state: dict, shared_state_lock: threading.Lock):
    UDP_IP, UDP_PORT = ip, port
    CHUNK_SIZE = 1400                      # ~ MTU altı
    HEADER_FMT = '<LHB'                   # frame_id:uint32, chunk_id:uint16, is_last:uint8

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # HSV renk aralıkları
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])


    detected_obj = ""
    frame_id = 0
    try:
        print(f"{UDP_IP} adresine gönderim başladı")
        broadcast_started.set()
        while not stop_event.is_set():
            frame = picam2.capture_array()

            ####### GORUNTU ISLEME BASLADI ########
            blurred = cv2.GaussianBlur(frame, (5, 5), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)

            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

            for color_mask, shape_name, target_sides, color in [
                (red_mask, "Ucgen", 3, (0, 0, 255)),
                (blue_mask, "Altigen", 6, (255, 0, 0))
            ]:
                contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    epsilon = 0.02 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    if len(approx) == target_sides and is_equilateral(approx):
                        cv2.drawContours(frame, [approx], 0, color, 2)
                        x, y = approx[0][0]
                        cv2.putText(frame, shape_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        detected_obj = shape_name
                        print(detected_obj)

            if detected_obj:
                with shared_state_lock:
                    shared_state["last_object"] = detected_obj
                    shared_state["timestamp"] = time.time()

            _, buf = cv2.imencode('.jpg', frame)
            data = buf.tobytes()
            total_chunks = ceil(len(data) / CHUNK_SIZE)
            ###### GORUNTU ISLEME BITTI ###########

            for chunk_id in range(total_chunks):
                start = chunk_id * CHUNK_SIZE
                end = start + CHUNK_SIZE
                chunk = data[start:end]
                is_last = 1 if chunk_id == total_chunks - 1 else 0
                header = struct.pack(HEADER_FMT, frame_id, chunk_id, is_last)
                sock.sendto(header + chunk, (UDP_IP, UDP_PORT))

            frame_id = (frame_id + 1) & 0xFFFFFFFF
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Ctrl+C ile çıkıldı.")

    finally:
        # Kamera ve soketi kapat
        print("Program sonlandırıldı.")
        picam2.stop()
        sock.close()


if len(sys.argv) != 5:
    print("Usage: python main.py <connection_string> <drone_id> <ip> <port>")
    sys.exit(1)


stop_event = threading.Event()
broadcast_started = threading.Event()
shared_state = {"last_object": None, "timestamp": 0}
shared_state_lock = threading.Lock()

dropped_objects = []

# PiCamera2'yi başlat ve yapılandır
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()
time.sleep(2)  # Kamera başlatma süresi için bekle

threading.Thread(target=image_recog_new, args=(picam2, sys.argv[3], int(sys.argv[4]), stop_event, broadcast_started, shared_state, shared_state_lock), daemon=True).start()

magnet_control(True, True)
print("mıknatıslar açık")

vehicle = Vehicle(sys.argv[1])
DRONE_ID = int(sys.argv[2])
ALT = 5

merkez = (40.711, 30.02, ALT)

second_tarama = True
second_tarama_yapildi = False

area_meter = 10
distance_meter = 2

drone_locs = vehicle.scan_area_wpler(center_loc=merkez, alt=ALT, area_meter=area_meter, distance_meter=distance_meter)
print(f"Birinci tarama wp sayısı: {len(drone_locs)}")

try:
    while not stop_event.is_set() and not broadcast_started.is_set():
        time.sleep(0.5)

    rotate_servo(0)
    print("servo duruyor")

    vehicle.set_mode("GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)

    home_pos = vehicle.get_pos(drone_id=DRONE_ID)
    print(f"{DRONE_ID}>> Kalkış tamamlandı")

    current_loc = 0
    vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)

    with shared_state_lock:
        shared_state["last_object"] = None  # tekrar tetiklenmesini engelle

    start_time = time.time()
    while not stop_event.is_set():
        with shared_state_lock:
            obj = shared_state["last_object"]
            ts = shared_state["timestamp"]

        if obj:
            print(obj)
            if dropped_objects != []:
                print(dropped_objects)
            if obj == "Ucgen" and obj not in dropped_objects:
                print("Üçgen Tespit edildi")

                pos = vehicle.get_pos(drone_id=DRONE_ID)

                vehicle.go_to(loc=pos, alt=ALT, drone_id=DRONE_ID)
                while not stop_event.is_set() and not vehicle.on_location(loc=pos, seq=0, sapma=0.5, drone_id=DRONE_ID):
                    time.sleep(0.5)

                time.sleep(3)
                print("mıknatıs2 kapatıldı")
                time.sleep(2)

                vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
                print("Yük 2 bırakıldı tarama devam ediyor...")
                vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)

                dropped_objects.append(obj)

                with shared_state_lock:
                    shared_state["last_object"] = None  # tekrar tetiklenmesini engelle
                start_time = time.time()
            
            if obj == "Altigen" and obj not in dropped_objects:
                print("Altıgen Tespit edildi")

                pos = vehicle.get_pos(drone_id=DRONE_ID)

                vehicle.go_to(loc=pos, alt=ALT, drone_id=DRONE_ID)
                while not stop_event.is_set() and not vehicle.on_location(loc=pos, seq=0, sapma=0.5, drone_id=DRONE_ID):
                    time.sleep(0.5)

                time.sleep(3)
                print("mıknatıs1 kapatıldı")
                time.sleep(2)
                
                vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
                print("Yük 1 bırakıldı tarama devam ediyor...")
                vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)

                dropped_objects.append(obj)

                with shared_state_lock:
                    shared_state["last_object"] = None  # tekrar tetiklenmesini engelle
                start_time = time.time()
        
        if vehicle.on_location(loc=drone_locs[current_loc], seq=0, sapma=1, drone_id=DRONE_ID) and (obj == None or obj in dropped_objects):
            start_time = time.time()
            print(f"{DRONE_ID}>> drone {current_loc + 1} ulasti")
            if current_loc + 1 == len(drone_locs):
                if second_tarama and second_tarama_yapildi == False:
                    print("İkinci tarama baslıyor")
                    second_tarama_yapildi = True
                    distance_meter /= 2
                    drone_locs = vehicle.scan_area_wpler(center_loc=merkez, alt=ALT, area_meter=area_meter, distance_meter=distance_meter)
                    current_loc = 0

                    print(f"İkinci tarama wp sayısı: {len(drone_locs)}")

                    vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)
                else:
                    print(f"{DRONE_ID}>> Drone taramayı bitirdi")
                    break
            else:
                current_loc += 1
                vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)
                print(f"{DRONE_ID}>> {current_loc + 1}/{len(drone_locs)}. konuma gidiyor...")

        time.sleep(0.05)
    
    print(f"Algilanan objeler: {dropped_objects}")
    vehicle.rtl(takeoff_pos=home_pos, alt=ALT, drone_id=DRONE_ID)

except KeyboardInterrupt:
    print("Klavye ile çıkış yapıldı")
    failsafe(vehicle)

except Exception as e:
    failsafe(vehicle)
    print("Hata:", e)

finally:
    vehicle.vehicle.close()
    cleanup()
    print("GPIO temizlendi, bağlantı kapatıldı")

