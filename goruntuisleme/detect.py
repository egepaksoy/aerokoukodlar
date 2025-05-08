#! GIBI
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
import keyboard

model_name = "best.pt"
model = YOLO("./models/" + model_name)

orta_pozisyon_orani = (0.4)

cap = cv2.VideoCapture(0) 

applicated_classes = []

if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

try:
    while True:
        ret, frame = cap.read()
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

                    # Sınıf ve güven skorunu al
                    cls = int(box.cls[0].item())
                    conf = box.conf[0].item()

                    # Sınırlayıcı kutu koordinatlarını al
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    # Sınıf adını al
                    class_name = model.names[cls]

                    if keyboard.is_pressed("c") and class_name not in applicated_classes and center_image(konumu, ekran_orani, orta_pozisyon_orani)["x"] == "Merkezde" and center_image(konumu, ekran_orani, orta_pozisyon_orani)["y"] == "Merkezde":
                        applicated_classes.append(class_name)
                        cv2.putText(frame, f"{class_name} sınıfı eklendi", (0, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                    box_color = (0, 255, 0)

                    # Bilgileri ekrana yazdır
                    print(f"Sınıf: {class_name}, Güven: {conf:.2f}, Konum: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}")
                    
                    # Nesneyi çerçeve içine al ve etiketle
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), box_color, 2)
                    cv2.putText(frame, f"{class_name} {conf:.2f}", (int(x1), int(y1 - 10)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
            cv2.imshow('YOLOv8 Canlı Tespit', frame)  # Görüntüyü göster
                
        # Çıkış için 'q' tuşuna basılması beklenir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
except KeyboardInterrupt:
    print("Ctrl+C ile çıkıldı.")

finally:
    print("Program sonlandırıldı.")
    cv2.destroyAllWindows()  # Tüm OpenCV pencerelerini kapat
