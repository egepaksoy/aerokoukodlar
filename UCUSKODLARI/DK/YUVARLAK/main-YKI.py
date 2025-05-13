import time
import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import Vehicle
import threading
from ultralytics import YOLO
import cv2
import numpy as np
import struct
import json
import socket
import queue


########### GORUNTU ISLEME ###############
def visualise_results(frame, box):
    # Sınıf ve güven skorunu al
    cls = int(box.cls[0].item())
    conf = box.conf[0].item()

    # Sınırlayıcı kutu koordinatlarını al
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
    konumu = (x1 + (x2-x1)/2, y1 + (y2-y1)/2)

    # Sınıf adını al
    class_name = model.names[cls]

    # Nesneyi çerçeve içine al ve etiketle
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,0, 255), 2)
    cv2.circle(frame, (int(konumu[0]), int(konumu[1])), 5, (0, 0, 255), -1)

    cv2.putText(frame, f"{class_name} {conf:.2f}", (int(x1), int(y1 - 10)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
    return class_name, (x1, y1, x2, y2)

def is_centered(xyxy, ekran_orani, orta_pozisyon_orani: float = 0.4):
    x, y = (xyxy[0] + (xyxy[2] - xyxy[0]) / 2), (xyxy[1] + (xyxy[3] - xyxy[1]) / 2)
    ekran_genislik, ekran_yukseklik = ekran_orani
    # Merkezdeki alanın sınırlarını belirle     baslangıc, bitis
    x_orta_genisligi = ekran_genislik * orta_pozisyon_orani
    y_orta_genisligi = ekran_yukseklik * orta_pozisyon_orani

    x_uzaklik = 0
    y_uzaklik = 0

    if x > ekran_genislik * (0.5 + orta_pozisyon_orani / 2):
        x_uzaklik = x - ekran_genislik * (0.5 + orta_pozisyon_orani / 2)
    elif x < ekran_genislik * (0.5 - orta_pozisyon_orani / 2):
        x_uzaklik = x - ekran_genislik * (0.5 - orta_pozisyon_orani / 2)
    
    if y > ekran_yukseklik * (0.5 + orta_pozisyon_orani / 2):
        y_uzaklik = y - ekran_yukseklik * (0.5 + orta_pozisyon_orani / 2)
    elif y < ekran_yukseklik * (0.5 - orta_pozisyon_orani / 2):
        y_uzaklik = y - ekran_yukseklik * (0.5 - orta_pozisyon_orani / 2)
    
    return float(x_uzaklik), float(y_uzaklik)

def show_proccesed_image(config):
    #!!! zehranın son yaptıgı kod tamamı gelcek !!!#
    '''
    yapı:
    while:
        send_to'dan once->xy koordinatlarını al
    '''
    UDP_IP = config["UDP"]["ip"]  # Alıcı bilgisayarın IP adresi
    UDP_PORT = config["UDP"]["port"]  # Alıcı bilgisayarın port numarası
    # 61440
    PACKET_SIZE = 60000  # UDP paket boyutu, 60 KB

    # UDP soketi oluştur
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"format": "RGB888", "size": (640, 480)}))
    picam2.start()
    time.sleep(2)  # Kamera başlatma süresi için bekle

    frame_counter = 0  # Çerçeve sayacını başlat

    total_frame = 0
    frame_time = time.time()
    try:
        while True:
            # Kamera görüntüsünü yakala
            frame = picam2.capture_array()
            # Görüntüyü JPEG formatında sıkıştır
            _, buffer = cv2.imencode('.jpg', frame)
            buffer = buffer.tobytes()  # Veriyi baytlara dönüştür
            buffer_size = len(buffer)  # Verinin boyutunu al

            # Veriyi parçalara böl ve gönder
            for i in range(0, buffer_size, PACKET_SIZE):
                end = i + PACKET_SIZE
                if end > buffer_size:
                    end = buffer_size
                packet = struct.pack('<L', frame_counter) + buffer[i:end]
                sock.sendto(packet, (UDP_IP, UDP_PORT))

            # Son paketle bir "son" işareti gönder
            sock.sendto(struct.pack('<L', frame_counter) + b'END', (UDP_IP, UDP_PORT))

            if frame_counter == 20000:
                frame_counter = 0
            frame_counter += 1  # Çerçeve sayacını artır
            total_frame += 1

            if time.time() - frame_time >= 0.1:
                print(f"FPS: {total_frame / (time.time() - frame_time)}")
                total_frame = 0
                frame_time = time.time()

    except KeyboardInterrupt:
        print("Ctrl+C ile çıkıldı.")

    finally:
        # Kamera ve soketi kapat
        print("Program sonlandırıldı.")
        picam2.stop()
        sock.close()


def image_processing_udp_YOLO(model, config):
    orta_pozisyon_orani = (0.2)

    # Kullanıcıdan IP adresi ve port numarasını komut satırından al
    UDP_IP = "0.0.0.0"  # Alıcı bilgisayarın IP adresi
    UDP_PORT = int(config["UDP"]["port"])  # Alıcı bilgisayarın port numarası
    BUFFER_SIZE = 65536  # UDP tampon boyutu, 64 KB

    try:
        # UDP soketi oluştur ve belirtilen IP ve portta dinlemeye başla
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        buffer = b''  # Gelen veri parçalarını depolamak için tampon
        current_frame = -1  # Geçerli çerçeve numarasını takip etmek için sayaç

        total_frame = 0

        frame_time = time.time()
        fps = 0
        while not stop_event.is_set():
            data, addr = sock.recvfrom(BUFFER_SIZE)  # Maksimum UDP paket boyutu kadar veri al
            
            # Çerçeve numarasını çöz
            frame_number = struct.unpack('<L', data[:4])[0]
            packet_data = data[4:]

            if frame_number != current_frame:
                if buffer:
                    # Görüntüyü verinin tamamı alındığında oluştur
                    npdata = np.frombuffer(buffer, dtype=np.uint8)
                    frame = cv2.imdecode(npdata, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        ekran_orani = (frame.shape[1], frame.shape[0])

                        results = model(frame)
                        for r in results:
                            boxes = r.boxes
                            for box in boxes:
                                if box.conf[0] < 0.90:
                                    continue

                                class_name, xyxy = visualise_results(frame, box)

                                cv2.putText(frame, f"center_range: {is_centered(xyxy, ekran_orani, orta_pozisyon_orani)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                                image_queue.put((class_name, is_centered(xyxy, ekran_orani, orta_pozisyon_orani)))

                        cv2.rectangle(frame, (int(ekran_orani[0] * (0.5 - orta_pozisyon_orani / 2)), int(ekran_orani[1] * (0.5 - orta_pozisyon_orani / 2))), (int(ekran_orani[0] * (0.5 + orta_pozisyon_orani / 2)), int(ekran_orani[1] * (0.5 + orta_pozisyon_orani / 2))), (255, 0, 0), 2)


                        if time.time() - frame_time >= 1:
                            fps = total_frame / (time.time() - frame_time)
                            total_frame = 0
                            frame_time = time.time()

                        cv2.putText(frame, f"{fps}", (0, 25), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                        cv2.imshow('YOLOv8 Canlı Tespit', frame)  # Görüntüyü göster
                    
                    buffer = b''  # Yeni görüntü için tamponu sıfırla

                current_frame = frame_number  # Geçerli çerçeve numarasını güncelle
                total_frame += 1
            
            if packet_data == b'END':
                # Son paket işareti, çerçevenin sonu
                continue
            
            buffer += packet_data  # Gelen veri parçasını tampona ekle

            # Çıkış için 'q' tuşuna basılması beklenir
            if cv2.waitKey(1) & 0xFF == ord('q') or yuk_birakildi_event.is_set():
                break
                
    finally:
        print("Program sonlandırıldı.")
        cv2.destroyAllWindows()  # Tüm OpenCV pencerelerini kapat
        sock.close()  # Soketi kapat


def image_processing_local_YOLO(model):
    orta_pozisyon_orani = (0.2)

    cap = cv2.VideoCapture(0) 

    if not cap.isOpened():
        print("Kamera açılamadı!")
        exit()

    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            ekran_orani = (frame.shape[1], frame.shape[0])

            if not ret:
                print("Kare okunamadı!")
                break

            if frame is not None:
                results = model(frame)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        if box.conf[0] < 0.90:
                            continue

                        class_name, xyxy = visualise_results(frame, box)

                        cv2.putText(frame, f"center_range: {is_centered(xyxy, ekran_orani, orta_pozisyon_orani)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                        image_queue.put((class_name, is_centered(xyxy, ekran_orani, orta_pozisyon_orani)))

                cv2.rectangle(frame, (int(ekran_orani[0] * (0.5 - orta_pozisyon_orani / 2)), int(ekran_orani[1] * (0.5 - orta_pozisyon_orani / 2))), (int(ekran_orani[0] * (0.5 + orta_pozisyon_orani / 2)), int(ekran_orani[1] * (0.5 + orta_pozisyon_orani / 2))), (255, 0, 0), 2)
                cv2.imshow('YOLOv8 Canlı Tespit', frame)  # Görüntüyü göster
            
            
            # Çıkış için 'q' tuşuna basılması beklenir
            if cv2.waitKey(1) & 0xFF == ord('q') or yuk_birakildi_event.is_set():
                break
            
    finally:
        print("Program sonlandırıldı.")
        cap.release()  # Kamerayı serbest bırak
        cv2.destroyAllWindows()  # Tüm OpenCV pencerelerini kapat



def failsafe(vehicle, home_pos=None, config: json=None):
    def failsafe_drone_id(vehicle, drone_id, home_pos=None):
        if home_pos == None:
            print(f"{drone_id}>> Failsafe alıyor")
            vehicle.set_mode(mode="RTL", drone_id=drone_id)

        # guıdedli rtl
        else:
            print(f"{drone_id}>> Failsafe alıyor")
            vehicle.set_mode(mode="GUIDED", drone_id=drone_id)

            alt = 5
            if config != None:
                if "DRONE" in config:
                    if "rtl-alt" in config["DRONE"]:
                        alt = config["DRONE"]["rtl-alt"]
            
            vehicle.go_to(loc=home_pos, alt=alt, drone_id=DRONE_ID)

            start_time = time.time()
            while True:
                if time.time() - start_time > 3:
                    print(f"{drone_id}>> RTL Alıyor...")
                    start_time = time.time()

                if vehicle.on_location(loc=home_pos, seq=0, sapma=1, drone_id=DRONE_ID):
                    print(f"{DRONE_ID}>> iniş gerçekleşiyor")
                    vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
                    break

    thraeds = []
    for d_id in vehicle.drone_ids:
        args = (vehicle, d_id)
        if home_pos != None:
            args = (vehicle, d_id, home_pos)

        thrd = threading.Thread(target=failsafe_drone_id, args=args)
        thrd.start()
        thraeds.append(thrd)


    for t in thraeds:
        t.join()

    print(f"{vehicle.drone_ids} id'li Drone(lar) Failsafe aldi")


############### GÖREV ###############
config = json.load(open("./config.json", "r"))
stop_event = threading.Event()
yuk_birakildi_event = threading.Event()

model_name = config["UDP"]["model-path"]
model = YOLO(model_name)

image_queue = queue.Queue()
#!img_processing_thread = threading.Thread(target=image_processing_udp_YOLO, args=(model, config), daemon=True)
img_processing_thread = threading.Thread(target=image_processing_local_YOLO, args=(model,), daemon=True)
img_processing_thread.start()

on_mission = False
yuk_birakildi = False

vehicle = Vehicle(config["DRONE"]["path"])

start_time = time.time()

pid_val = 1

ALT = config["DRONE"]["alt"]
DRONE_ID = config["DRONE"]["id"] # drone id
direk_locs = config["DRONE"]["direk-locs"]

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)
    home_pos = vehicle.get_pos(drone_id=DRONE_ID)
    
    print(f"{DRONE_ID}>> takeoff yaptı")

    # TODO: daire cizme kodu ekle
    vehicle.go_to(loc=direk_locs[0], alt=ALT, drone_id=DRONE_ID)
    direk_count = 0

    start_time = time.time()
    on_miss_time = 0
    while not stop_event.is_set():
        if time.time() - start_time >= 3:
            print("Taranıyor..")
            start_time = time.time()
        
        if not image_queue.empty() and yuk_birakildi == False:
            class_name, (x_uzaklik, y_uzaklik) = image_queue.get_nowait()
            y_uzaklik *= -1 #! terse gidiyordu
            print(f"\n\n{DRONE_ID}>> DRONE {class_name} hedefini algıladı")
            print(f"x: {x_uzaklik}, y: {y_uzaklik}\n\n")

            if x_uzaklik < 0:
                x_rota = -1 * pid_val
            elif x_uzaklik > 0:
                x_rota = 1 * pid_val
            else:
                x_rota = 0
            if y_uzaklik < 0:
                y_rota = -1 * pid_val
            elif y_uzaklik > 0:
                y_rota = 1 * pid_val
            else:
                y_rota = 0
            
            print(f"{x_rota}|{y_rota}")
            
            on_mission = True

            if on_miss_time == 0 and abs(x_rota) + abs(y_rota) == 0:
                on_miss_time = time.time()
                if pid_val > 0.07:
                    pid_val /= 2

            if abs(x_rota) + abs(y_rota) != 0:
                on_miss_time = 0
        
        if on_mission:
            rota = (y_rota, x_rota, 0)
            vehicle.move_drone(rota, drone_id=DRONE_ID)
            
            if time.time() - on_miss_time > 4 and on_miss_time != 0:
                print("Yük bırakıldı")
                on_mission = False
                yuk_birakildi = True
                yuk_birakildi_event.set()
        
        if on_mission == False:
            if vehicle.on_location(direk_locs[0], seq=0, drone_id=DRONE_ID) and direk_count == 0:
                vehicle.go_to(loc=direk_locs[1], alt=ALT, drone_id=DRONE_ID)
                direk_count = 1

            if vehicle.on_location(direk_locs[1], seq=0, drone_id=DRONE_ID) and direk_count == 1:
                break
        
        if yuk_birakildi:
            print("Yük bırakıldı")
            break
        
    if yuk_birakildi:
        vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
    else:
        vehicle.rtl(takeoff_pos=home_pos, alt=config["DRONE"]["rtl-alt"], drone_id=DRONE_ID)
    
    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")
    if "home_pos" in locals():
        failsafe(vehicle, home_pos, config)
    else:
        failsafe(vehicle)
    if not stop_event.is_set():
        stop_event.set()

except Exception as e:
    if "home_pos" in locals():
        failsafe(vehicle, home_pos, config)
    else:
        failsafe(vehicle)
    if not stop_event.is_set():
        stop_event.set()
    print(e)

finally:
    if not stop_event.is_set():
        stop_event.set()
    vehicle.vehicle.close()
    cv2.destroyAllWindows()