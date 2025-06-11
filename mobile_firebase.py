import cv2
import numpy as np
import urllib.request as u
from face_recognition_manager import FaceRecognitionManager
import signal
import sys

def signal_handler(sig, frame):
    """Ctrl+C ile çıkış yapıldığında temizlik yapar"""
    print('\nÇıkış yapılıyor...')
    face_manager.cleanup()
    cv2.destroyAllWindows()
    sys.exit(0)

# Signal handler'ı kaydet
signal.signal(signal.SIGINT, signal_handler)

# Mobil kamera URL'inizi buraya girin
MOBILE_URL = 'http://192.168.0.102:8080/shot.jpg'

# Firebase service account dosyası yolu (isteğe bağlı)
SERVICE_ACCOUNT_PATH = "firebase-service-account.json"  # Dosya varsa

# Yüz tanıma yöneticisini başlat
face_manager = FaceRecognitionManager(
    faces_directory='faces',
    firebase_service_account=SERVICE_ACCOUNT_PATH if SERVICE_ACCOUNT_PATH else None
)

print("Mobil Kamera Yüz tanıma başlatıldı. Çıkmak için 'q' tuşuna basın.")
print("Firebase güncellemeleri konsol çıktısında görüntülenecek.")

frame_count = 0
process_every_n_frames = 2  # Her 2 frame'de bir işle

try:
    while True:
        try:
            # Mobil kameradan görüntü al
            video_url = u.urlopen(MOBILE_URL)
            video_data = np.array(bytearray(video_url.read()), dtype=np.uint8)
            frame = cv2.imdecode(video_data, -1)
            
            if frame is None:
                print("Mobil kameradan görüntü alınamadı!")
                continue
            
            # Her n frame'de bir işle
            if frame_count % process_every_n_frames == 0:
                frame = face_manager.process_frame(frame)
            
            # Görüntüyü göster
            cv2.imshow('Mobil Firebase Yüz Tanıma', frame)
            
            frame_count += 1
            
            # 'q' tuşu ile çıkış
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        except Exception as e:
            print(f"Frame işleme hatası: {e}")
            continue

except KeyboardInterrupt:
    print("\nKullanıcı tarafından durduruldu")

finally:
    # Temizlik
    face_manager.cleanup()
    cv2.destroyAllWindows()
    print("Uygulama kapatıldı.")