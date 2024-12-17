#! GIBI
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time

def is_centered(konum, ekran_orani, orta_pozisyon_orani: float = 0.4) -> bool:
    x, y = konum
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
    
    return x_uzaklik, y_uzaklik


def center_image(konum, ekran_orani, orta_pozisyon_orani: float = 0.4):
    x_uzakligi, y_uzakligi = is_centered(konum, ekran_orani, orta_pozisyon_orani)

    islem = {"x": "", "y": ""}

    if x_uzakligi == 0:
        islem["x"] = "Merkezde"
    elif x_uzakligi > 0:
        islem["x"] = f"Sola git: {x_uzakligi:.2f}"
    else:
        islem["x"] = f"Saga git: {x_uzakligi:.2f}"

    if y_uzakligi == 0:
        islem["y"] = "Merkezde"
    
    elif y_uzakligi > 0:
        islem["y"] = f"Asagiya git: {y_uzakligi:.2f}"
    else:
        islem["y"] = f"Yukariya git: {y_uzakligi:.2f}"
    
    return islem

model_name = "kullanilcak.pt"
model = YOLO("../models/" + model_name)

orta_pozisyon_orani = (0.4)

cap = cv2.VideoCapture(0) 

if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

try:
    total_frame = 0
    
    frame_time = time.time()
    fps = 0
    while True:
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
                    # Sınırlayıcı kutu koordinatlarını al
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    # Sınıf ve güven skorunu al
                    cls = int(box.cls[0].item())
                    conf = box.conf[0].item()

                    # Sınıf adını al
                    class_name = model.names[cls]

                    # Bilgileri ekrana yazdır
                    print(f"Sınıf: {class_name}, Güven: {conf:.2f}, Konum: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}")
                    konumu = (x1 + (x2-x1)/2, y1 + (y2-y1)/2)
                    
                    print(center_image(konumu, ekran_orani, orta_pozisyon_orani))

                    # Nesneyi çerçeve içine al ve etiketle
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                    cv2.circle(frame, (int(konumu[0]), int(konumu[1])), 5, (0, 0, 255), -1)

                    cv2.putText(frame, f"{class_name} {conf:.2f}", (int(x1), int(y1 - 10)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    cv2.putText(frame, f"{center_image(konumu, ekran_orani, orta_pozisyon_orani)}", (int(ekran_orani[0] * (0.5 - orta_pozisyon_orani / 2)), int(ekran_orani[1] * (0.5 + orta_pozisyon_orani / 2))), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3)
                    

            if time.time() - frame_time:
                fps = total_frame / (time.time() - frame_time)
                total_frame = 0
                frame_time = time.time()

            cv2.putText(frame, f"{fps:.1f}", (0, 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.rectangle(frame, (int(ekran_orani[0] * (0.5 - orta_pozisyon_orani / 2)), int(ekran_orani[1] * (0.5 - orta_pozisyon_orani / 2))), (int(ekran_orani[0] * (0.5 + orta_pozisyon_orani / 2)), int(ekran_orani[1] * (0.5 + orta_pozisyon_orani / 2))), (255, 0, 0), 2)
            cv2.imshow('YOLOv8 Canlı Tespit', frame)  # Görüntüyü göster
                
            total_frame += 1

        # Çıkış için 'q' tuşuna basılması beklenir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
except KeyboardInterrupt:
    print("Ctrl+C ile çıkıldı.")

finally:
    print("Program sonlandırıldı.")
    cv2.destroyAllWindows()  # Tüm OpenCV pencerelerini kapat