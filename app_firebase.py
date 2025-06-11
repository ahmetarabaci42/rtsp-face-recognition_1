import cv2
from face_recognition_manager import FaceRecognitionManager
import signal
import sys

def signal_handler(sig, frame):
    """Ctrl+C ile çıkış yapıldığında temizlik yapar"""
    print('\nÇıkış yapılıyor...')
    face_manager.cleanup()
    video.release()
    cv2.destroyAllWindows()
    sys.exit(0)

# Signal handler'ı kaydet
signal.signal(signal.SIGINT, signal_handler)

# Firebase service account dosyası yolu (isteğe bağlı)
# Eğer environment variables kullanıyorsanız None bırakın
SERVICE_ACCOUNT_PATH = "firebase-service-account.json"  # Dosya varsa

# Yüz tanıma yöneticisini başlat
face_manager = FaceRecognitionManager(
    faces_directory='faces',
    firebase_service_account=SERVICE_ACCOUNT_PATH if SERVICE_ACCOUNT_PATH else None
)

# Webcam'i başlat
video = cv2.VideoCapture(0)

print("Yüz tanıma başlatıldı. Çıkmak için 'q' tuşuna basın.")
print("Firebase güncellemeleri konsol çıktısında görüntülenecek.")

frame_count = 0
process_every_n_frames = 2  # Her 2 frame'de bir işle (performans için)

try:
    while True:
        ret, frame = video.read()
        if not ret:
            print("Kamera görüntüsü alınamadı!")
            break
        
        # Her frame'i işleme (performans için sınırlandırılabilir)
        if frame_count % process_every_n_frames == 0:
            frame = face_manager.process_frame(frame)
        
        # Görüntüyü göster
        cv2.imshow('Firebase Yüz Tanıma', frame)
        
        frame_count += 1
        
        # 'q' tuşu ile çıkış
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Hata oluştu: {e}")

finally:
    # Temizlik
    face_manager.cleanup()
    video.release()
    cv2.destroyAllWindows()
    print("Uygulama kapatıldı.")