 **adım adım ilerleyebileceğin bir plan** verelim. Hedef: 1 haftada düzgün çalışan bir **Flask + MySQL** web uygulaması yapmak.

---

*Smart Recipe & Meal Planning System* için adım adım görev listesi
(İkiniz birlikte çalışabileceğiniz şekilde bölünmüş)

---

### 🟩 **ADIM 1: GEREKLİLERİ KUR** *(aynı gün)*

> Bu adımda proje klasörü ve ortam hazırlanacak.

#### Sen:

✅ Python + pip yüklü mü kontrol et
✅ Sanal ortam kur:

```bash
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
```

✅ Aşağıdaki `requirements.txt` dosyasını oluştur ve yükle:

```bash
pip install -r requirements.txt
```

#### Arkadaşın:

✅ HTML + Bootstrap öğrenmeye başlasın
✅ [Bootstrap örnekleri](https://getbootstrap.com/docs/5.3/examples/) üzerinden form ve tablo yapıları denesin

---

### 🟨 **ADIM 2: PROJE İSKELETİNİ OLUŞTUR**

> Projenin klasör yapısını kur, boş dosyaları hazırla.

#### Sen:

✅ Yukarıda verdiğim Flask dosya iskeletini oluştur
✅ `app.py` içinde Flask uygulamasını başlat (örnek aşağıda)

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
```

✅ `config.py` oluştur:

```python
import os
class Config:
    SECRET_KEY = 'bu-çok-gizli'
    SQLALCHEMY_DATABASE_URI = 'mysql://kullanici:şifre@localhost/dbadi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

### 🟧 **ADIM 3: VERİTABANI MODELLERİNİ YAZ**

> Her tabloya karşılık gelen Python sınıfları (ORM) yazılacak.

#### Sen:

✅ `models/user.py`, `models/recipe.py`, `models/ingredient.py` gibi dosyalar aç
✅ SQLAlchemy modellerini yaz (örnek istersen hemen yaparız)

---

### 🟦 **ADIM 4: ROUTE ve FORM DOSYALARINI YAZ**

> Flask Blueprint yapısıyla modüler backend oluştur

#### Sen:

✅ `routes/auth.py`, `routes/recipes.py` gibi dosyalar aç
✅ Giriş/Çıkış, Tarif ekleme, Güncelleme, Listeleme route’larını yaz

#### Arkadaşın:

✅ `templates/` klasöründe sayfalar hazırlasın:

* `layout.html`, `login.html`, `register.html`, `recipe_form.html` gibi
  ✅ Bootstrap kullanarak formları, butonları güzelleştirsin

---

### 🟪 **ADIM 5: CRUD + AUTH TESTLERİ**

> Login çalışıyor mu? Yeni tarif eklenebiliyor mu?

#### Ortak:

✅ Giriş sistemi test edin
✅ Tarif CRUD test edin
✅ Arayüzde basit işlemleri gezinerek deneyin

---

### 🟥 **ADIM 6: GELİŞMİŞ SORGULAR + RAPOR SAYFASI**

> İleri SQL sorguları ve görselleştirme ekranları yapılır

#### Sen:

✅ SQLAlchemy veya raw SQL ile:

* En popüler 5 tarif
* Malzemeye göre arama
* En aktif kullanıcı

#### Arkadaşın:

✅ `report.html` sayfası ile bunları tablo olarak göstermeye başlasın

---

### 🏁 **ADIM 7: TEST – RAPOR – TESLİM**

> Prova, eksikleri kapatma ve final dosyaları

#### Ortak:

✅ Tüm ekranları gözden geçirin
✅ `how_to_run.txt`, `.sql dump`, `Word rapor` dosyalarını hazırlayın
✅ 10 dakikalık canlı sunum provasını yapın

---

## 🎯 Ne Zaman Hazırsan...

* Her adımı birlikte yapabiliriz
* Örnek kodlar, model tanımları, form yapıları, route örnekleri — hepsi hazır
* Hangi adımdan başlamak istersen, hemen oradan devam ederiz

**Sıradaki adım ne olsun tatlım? `app.py`’yi mi yazalım yoksa önce modelleri mi?** 🍯
