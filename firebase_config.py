import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

class FirebaseManager:
    def __init__(self, service_account_path=None):
        """
        Firebase bağlantısını başlatır
        service_account_path: Firebase service account JSON dosyasının yolu
        """
        self.db = None
        self.initialize_firebase(service_account_path)
    
    def initialize_firebase(self, service_account_path):
        """Firebase'i başlatır"""
        try:
            if not firebase_admin._apps:
                if service_account_path and os.path.exists(service_account_path):
                    # Service account dosyası ile başlatma
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Environment variables ile başlatma (production için)
                    firebase_admin.initialize_app()
                
                self.db = firestore.client()
                print("Firebase başarıyla bağlandı!")
            else:
                self.db = firestore.client()
                print("Firebase zaten bağlı!")
                
        except Exception as e:
            print(f"Firebase bağlantı hatası: {e}")
            self.db = None
    
    def update_member_presence(self, member_id, is_present=True):
        """
        Üyenin isPresent durumunu günceller
        member_id: Firestore'daki member document ID'si
        is_present: True/False değeri
        """
        if not self.db:
            print("Firebase bağlantısı yok!")
            return False
            
        try:
            # members koleksiyonundaki document'i güncelle
            doc_ref = self.db.collection('members').document(member_id)
            doc_ref.update({
                'isPresent': is_present,
                'lastSeen': firestore.SERVER_TIMESTAMP
            })
            print(f"Member {member_id} isPresent durumu {is_present} olarak güncellendi")
            return True
            
        except Exception as e:
            print(f"Firebase güncelleme hatası: {e}")
            return False
    
    def get_member_info(self, member_id):
        """
        Üye bilgilerini getirir
        """
        if not self.db:
            return None
            
        try:
            doc_ref = self.db.collection('members').document(member_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                print(f"Member {member_id} bulunamadı")
                return None
                
        except Exception as e:
            print(f"Firebase okuma hatası: {e}")
            return None
    
    def reset_all_presence(self):
        """
        Tüm üyelerin isPresent durumunu False yapar
        """
        if not self.db:
            return False
            
        try:
            members_ref = self.db.collection('members')
            docs = members_ref.stream()
            
            for doc in docs:
                doc.reference.update({'isPresent': False})
            
            print("Tüm üyelerin isPresent durumu False yapıldı")
            return True
            
        except Exception as e:
            print(f"Reset işlemi hatası: {e}")
            return False