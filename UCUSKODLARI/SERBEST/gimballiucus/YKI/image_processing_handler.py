#! GIBI
import sys
import cv2
import socket
import numpy as np
import struct
from ultralytics import YOLO
import time
import queue
import threading

class Handler:
    def __init__(self):
        self.model = None
        self.proccessing = False
        self.is_running = True
        self.showing_image = True
    
    def local_camera(self, camera_path):
        cap = cv2.VideoCapture(camera_path)

        if not cap.isOpened():
            print(f"Dahili kamera {camera_path} açılamadı")
        
        start_time = time.time()
        while self.is_running:
            ret, frame = cap.read()

            if time.time() - start_time > 0.1 and self.proccessing:
                results = self.model(frame)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        if box.conf[0] < 0.90:
                            continue
                        # Sınırlayıcı kutu koordinatlarını al
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                        # Sınıf ve güven skorunu al
                        cls = int(box.cls[0].item())
                        conf = box.conf[0].item()

                        # Sınıf adını al
                        class_name = self.model.names[cls]

                        # Bilgileri ekrana yazdır
                        print(f"Sınıf: {class_name}, Güven: {conf:.2f}, Konum: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}")

                        # Nesneyi çerçeve içine al ve etiketle
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(frame, f"{class_name} {conf:.2f}", (int(x1), int(y1 - 10)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                start_time = time.time()
                        
            if self.showing_image:
                cv2.imshow("İşlenen görüntü", frame)

            # Çıkış için 'q' tuşuna basılması beklenir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def udp_camera(self, ip, port):
        BUFFER_SIZE = 65536
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, port))

        buffer = b''  # Gelen veri parçalarını depolamak için tampon
        current_frame = -1  # Geçerli çerçeve numarasını takip etmek için sayaç
        start_time = time.time()
        while self.is_running:
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
                        if time.time() - start_time > 0.1 and self.proccessing:
                            results = self.model(frame)
                            for r in results:
                                boxes = r.boxes
                                for box in boxes:
                                    if box.conf[0] < 0.90:
                                        continue
                                    # Sınırlayıcı kutu koordinatlarını al
                                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                                    # Sınıf ve güven skorunu al
                                    cls = int(box.cls[0].item())
                                    conf = box.conf[0].item()

                                    # Sınıf adını al
                                    class_name = self.model.names[cls]

                                    # Bilgileri ekrana yazdır
                                    print(f"Sınıf: {class_name}, Güven: {conf:.2f}, Konum: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}")

                                    # Nesneyi çerçeve içine al ve etiketle
                                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                    cv2.putText(frame, f"{class_name} {conf:.2f}", (int(x1), int(y1 - 10)), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                            start_time = time.time()
                        
                        # Çıkış için 'q' tuşuna basılması beklenir
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                        if self.showing_image:
                            cv2.imshow("İşlenen görüntü", frame)

                    buffer = b''  # Yeni görüntü için tamponu sıfırla

                current_frame = frame_number  # Geçerli çerçeve numarasını güncelle

            if packet_data == b'END':
                # Son paket işareti, çerçevenin sonu
                continue
            
            buffer += packet_data  # Gelen veri parçasını tampona ekle
    
    def show_image(self):
        self.showing_image = True
    
    def hide_image(self):
        self.showing_image = False
    
    def start_proccessing(self, model_path):
        self.proccessing = True
        if self.model == None:
            self.model = YOLO(model_path)
            print("model yuklendi")
    
    def stop_proccessing(self):
        self.proccessing = False