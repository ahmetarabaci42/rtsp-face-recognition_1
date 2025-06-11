from firebase_config import FirebaseManager
import time

def test_firebase_connection():
    """Firebase bağlantısını test eder"""
    print("Firebase bağlantısı test ediliyor...")
    
    # Firebase manager'ı başlat
    firebase_manager = FirebaseManager("firebase-service-account.json")
    
    if not firebase_manager.db:
        print("❌ Firebase bağlantısı başarısız!")
        return False
    
    print("✅ Firebase bağlantısı başarılı!")
    
    # Test member ID'si
    test_member_id = "test_member_123"
    
    try:
        # Test member'ı present yap
        print(f"Test: {test_member_id} present yapılıyor...")
        firebase_manager.update_member_presence(test_member_id, True)
        
        # Bilgileri oku
        member_info = firebase_manager.get_member_info(test_member_id)
        if member_info:
            print(f"Member bilgileri: {member_info}")
        
        # 3 saniye bekle
        time.sleep(3)
        
        # Test member'ı absent yap
        print(f"Test: {test_member_id} absent yapılıyor...")
        firebase_manager.update_member_presence(test_member_id, False)
        
        print("✅ Firebase test başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Firebase test hatası: {e}")
        return False

if __name__ == "__main__":
    test_firebase_connection()