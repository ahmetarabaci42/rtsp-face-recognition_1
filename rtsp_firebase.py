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

# RTSP URL'inizi buraya girin
RTSP_URL = 'rtsp://192.168.0.102:8080/h264_ulaw.sdp'

# Firebase service account dosyası yolu (isteğe bağlı)
SERVICE_ACCOUNT_PATH = "firebase-service-account.json"  # Dosya varsa

# Yüz tanıma yöneticisini başlat
face_manager = FaceRecognitionManager(
    faces_directory='faces',
    firebase_service_account=SERVICE_ACCOUNT_PATH if SERVICE_ACCOUNT_PATH else None
)

# RTSP stream'i başlat
video = cv2.VideoCapture(RTSP_URL)

if not video.isOpened():
    print(f"RTSP stream açılamadı: {RTSP_URL}")
    sys.exit(1)

print("RTSP Yüz tanıma başlatıldı. Çıkmak için 'q' tuşuna basın.")
print("Firebase güncellemeleri konsol çıktısında görüntülenecek.")

frame_count = 0
process_every_n_frames = 3  # Her 3 frame'de bir işle (RTSP için daha az sıklık)

try:
    while True:
        ret, frame = video.read()
        if not ret:
            print("RTSP stream'den görüntü alınamadı!")
            break
        
        # Her n frame'de bir işle
        if frame_count % process_every_n_frames == 0:
            frame = face_manager.process_frame(frame)
        
        # Görüntüyü göster
        cv2.imshow('RTSP Firebase Yüz Tanıma', frame)
        
        frame_count += 1
        
        # 'q' tuşu ile çıkış
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f'İşlenen toplam frame: {frame_count}')
            break

except Exception as e:
    print(f"Hata oluştu: {e}")

finally:
    # Temizlik
    face_manager.cleanup()
    video.release()
    cv2.destroyAllWindows()
    print("Uygulama kapatıldı.")