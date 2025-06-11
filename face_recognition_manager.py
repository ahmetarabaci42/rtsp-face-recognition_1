import os
import numpy as np
import face_rec
import cv2
from firebase_config import FirebaseManager

class FaceRecognitionManager:
    def __init__(self, faces_directory='faces', firebase_service_account=None):
        """
        Yüz tanıma yöneticisini başlatır
        faces_directory: Yüz resimlerinin bulunduğu klasör
        firebase_service_account: Firebase service account JSON dosyası yolu
        """
        self.faces_directory = faces_directory
        self.known_face_encodings = []
        self.known_face_names = []
        self.member_ids = []
        
        # Firebase bağlantısı
        self.firebase_manager = FirebaseManager(firebase_service_account)
        
        # Yüzleri yükle
        self.load_known_faces()
        
        # Başlangıçta tüm presence durumlarını sıfırla
        self.firebase_manager.reset_all_presence()
        
        # Tanınan kişileri takip etmek için set
        self.currently_present = set()
    
    def load_known_faces(self):
        """
        faces klasöründeki resimleri yükler ve encoding'lerini oluşturur
        Dosya adları member ID olarak kullanılır (örn: member123.jpg)
        """
        if not os.path.exists(self.faces_directory):
            print(f"Uyarı: {self.faces_directory} klasörü bulunamadı!")
            return
        
        print("Bilinen yüzler yükleniyor...")
        
        for filename in os.listdir(self.faces_directory):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Dosya adından member ID'yi al (uzantıyı çıkar)
                member_id = os.path.splitext(filename)[0]
                file_path = os.path.join(self.faces_directory, filename)
                
                try:
                    # Resmi yükle
                    image = face_rec.load_image_file(file_path)
                    
                    # Face encoding oluştur
                    encodings = face_rec.face_encodings(image)
                    
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.member_ids.append(member_id)
                        
                        # Firebase'den isim bilgisini al
                        member_info = self.firebase_manager.get_member_info(member_id)
                        if member_info and 'name' in member_info:
                            display_name = member_info['name']
                        else:
                            display_name = member_id
                        
                        self.known_face_names.append(display_name)
                        print(f"✓ {filename} yüklendi - Member ID: {member_id}, İsim: {display_name}")
                    else:
                        print(f"✗ {filename} - Yüz bulunamadı!")
                        
                except Exception as e:
                    print(f"✗ {filename} yüklenirken hata: {e}")
        
        print(f"Toplam {len(self.known_face_encodings)} yüz yüklendi")
    
    def process_frame(self, frame):
        """
        Frame'i işler ve yüz tanıma yapar
        """
        # Frame'i küçült (performans için)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Yüz konumlarını ve encoding'lerini bul
        face_locations = face_rec.face_locations(rgb_small_frame)
        face_encodings = face_rec.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        detected_member_ids = []
        
        for face_encoding in face_encodings:
            # Bilinen yüzlerle karşılaştır
            matches = face_rec.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            member_id = None
            
            # En yakın eşleşmeyi bul
            face_distances = face_rec.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                member_id = self.member_ids[best_match_index]
                detected_member_ids.append(member_id)
            
            face_names.append(name)
        
        # Firebase'de presence durumunu güncelle
        self.update_presence_status(detected_member_ids)
        
        # Frame'e çerçeve ve isim ekle
        self.draw_face_boxes(frame, face_locations, face_names)
        
        return frame
    
    def update_presence_status(self, detected_member_ids):
        """
        Tespit edilen member ID'lerin Firebase'deki isPresent durumunu günceller
        """
        # Yeni tespit edilen kişiler
        newly_detected = set(detected_member_ids) - self.currently_present
        
        # Artık görünmeyen kişiler
        no_longer_present = self.currently_present - set(detected_member_ids)
        
        # Yeni tespit edilenleri Firebase'de güncelle
        for member_id in newly_detected:
            self.firebase_manager.update_member_presence(member_id, True)
            print(f"🟢 {member_id} şimdi mevcut")
        
        # Artık görünmeyenleri Firebase'de güncelle
        for member_id in no_longer_present:
            self.firebase_manager.update_member_presence(member_id, False)
            print(f"🔴 {member_id} artık mevcut değil")
        
        # Mevcut durumu güncelle
        self.currently_present = set(detected_member_ids)
    
    def draw_face_boxes(self, frame, face_locations, face_names):
        """
        Frame üzerine yüz çerçeveleri ve isimleri çizer
        """
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Koordinatları orijinal boyuta çevir
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Yüz çerçevesi çiz
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # İsim etiketi çiz
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    
    def cleanup(self):
        """
        Uygulama kapanırken tüm presence durumlarını sıfırla
        """
        print("Temizlik yapılıyor...")
        self.firebase_manager.reset_all_presence()
        print("Tüm presence durumları sıfırlandı")