# Firebase Yüz Tanıma Sistemi Kurulum Rehberi

## 1. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

## 2. Firebase Kurulumu

### Seçenek A: Service Account Dosyası ile (Önerilen)
1. Firebase Console'dan projenize gidin
2. Project Settings > Service Accounts
3. "Generate new private key" butonuna tıklayın
4. İndirilen JSON dosyasını `firebase-service-account.json` olarak kaydedin

### Seçenek B: Environment Variables ile
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account.json"
```

## 3. Firestore Veritabanı Yapısı

Firestore'da `members` koleksiyonu oluşturun. Her member document'i şu yapıda olmalı:

```json
{
  "name": "Kişi Adı",
  "isPresent": false,
  "lastSeen": null
}
```

## 4. Yüz Resimlerini Hazırlayın

`faces/` klasörüne member ID'leri ile isimlendirilmiş resimler ekleyin:
- `member123.jpg`
- `user456.png`
- `person789.jpeg`

## 5. Uygulamayı Çalıştırın

### Webcam için:
```bash
python app_firebase.py
```

### RTSP Stream için:
```bash
python rtsp_firebase.py
```

### Mobil Kamera için:
```bash
python mobile_firebase.py
```

## 6. Önemli Notlar

- Uygulama başladığında tüm `isPresent` değerleri `false` yapılır
- Yüz tanındığında `isPresent=true` ve `lastSeen` güncellenir
- Yüz artık görünmediğinde `isPresent=false` yapılır
- Uygulama kapanırken tüm `isPresent` değerleri `false` yapılır

## 7. Sorun Giderme

### Firebase Bağlantı Sorunu:
- Service account dosyasının doğru yolda olduğundan emin olun
- Firebase projesinde Firestore'un aktif olduğunu kontrol edin

### Yüz Tanıma Sorunu:
- Resim dosyalarının `faces/` klasöründe olduğundan emin olun
- Resim kalitesinin yeterli olduğunu kontrol edin
- Dosya adlarının member ID ile eşleştiğinden emin olun

### Performans Optimizasyonu:
- `process_every_n_frames` değerini artırarak işlem sıklığını azaltabilirsiniz
- Kamera çözünürlüğünü düşürebilirsiniz