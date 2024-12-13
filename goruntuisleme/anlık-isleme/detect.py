import tensorflow as tf
import numpy as np
import cv2

# Eğitilmiş modeli yükle
model = tf.keras.models.load_model("./models/mobilenet_trained_model.h5")

# Sınıf adlarını manuel olarak tanımla (eğitim sırasında kullandığın klasör adlarına göre ayarla)
class_indices = {0: "trophy"}  # Örnek: {0: "nesne1", 1: "nesne2"}

# Girdi boyutları (MobileNetV2 için 224x224)
IMG_SIZE = (224, 224)

# Kamera akışı başlat
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

print("Kamera başlatıldı. Çıkış için 'q' tuşuna basın.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera görüntüsü alınamadı!")
        break

    # Görüntüyü modelin girdi boyutlarına yeniden boyutlandır
    resized_frame = cv2.resize(frame, IMG_SIZE)
    input_image = np.expand_dims(resized_frame, axis=0) / 255.0  # Normalleştirme

    # Tahmin yap
    predictions = model.predict(input_image)
    predicted_class = np.argmax(predictions)
    confidence = np.max(predictions)

    # Tahmini sınıf adını al
    class_name = class_indices.get(predicted_class, "Bilinmeyen")

    # Sonuçları görüntü üzerine yaz
    text = f"{class_name} ({confidence * 100:.2f}%)"
    cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Görüntüyü göster
    cv2.imshow("Nesne Tanıma", frame)

    # Çıkış için 'q' tuşuna bas
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
cap.release()
cv2.destroyAllWindows()
