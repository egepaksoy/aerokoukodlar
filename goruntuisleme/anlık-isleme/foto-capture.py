import cv2
import os

def main():
    # Kaydedilecek klasörü belirle
    base_dir = "captured_images"
    os.makedirs(base_dir, exist_ok=True)

    # Kullanıcıdan etiket (nesne adı) al
    label = input("Kaydedilecek nesne adı (ör: canta): ").strip()
    if not label:
        print("Etiket girmediniz, program sonlandırılıyor.")
        return

    label_dir = os.path.join(base_dir, label)
    os.makedirs(label_dir, exist_ok=True)

    # Kamera akışını başlat
    cap = cv2.VideoCapture(0)  # 0, varsayılan kamerayı temsil eder
    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    print("\nGörüntü yakalamak için 's' tuşuna basın. Çıkış için 'q' tuşuna basın.")
    img_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera görüntüsü alınamadı!")
            break

        # Canlı görüntüyü göster
        cv2.imshow("Kamera", frame)

        # Klavye girişlerini kontrol et
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # 's' tuşuna basıldığında kaydet
            img_count += 1
            img_name = os.path.join(label_dir, f"{label}_{img_count:03}.jpg")
            cv2.imwrite(img_name, frame)
            print(f"Görüntü kaydedildi: {img_name}")

        elif key == ord('q'):  # 'q' tuşuna basıldığında çık
            print("Çıkış yapılıyor...")
            break

    # Kaynakları serbest bırak
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
