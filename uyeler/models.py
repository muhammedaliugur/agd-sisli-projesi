# uyeler/models.py (NOT DEFTERİ MODÜLÜ EKLENMİŞ NİHAİ SÜRÜM)

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- MEVCUT MODELLERİN OLDUĞU GİBİ KORUNDU ---

class Komisyon(models.Model):
    ad = models.CharField(max_length=100, unique=True, verbose_name="Komisyon Adı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    class Meta:
        verbose_name = "Komisyon"
        verbose_name_plural = "Komisyonlar"
        ordering = ['ad']
    def __str__(self):
        return self.ad

class Profil(models.Model):
    class Rol(models.TextChoices):
        YETKILI = 'YETKILI', 'Yetkili'
        BIRIM_BASKANI = 'BIRIM_BASKANI', 'Birim Başkanı'
        UYE = 'UYE', 'Standart Üye'
    class Status(models.TextChoices):
        BEKLEMEDE = 'BEKLEMEDE', 'Onay Bekliyor'
        AKTIF = 'AKTIF', 'Aktif'
        REDDEDILDI = 'REDDEDILDI', 'Reddedildi'

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Kullanıcı", related_name='profil')
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.UYE, verbose_name="Kullanıcı Rolü")
    statü = models.CharField(max_length=20, choices=Status.choices, default=Status.BEKLEMEDE, verbose_name="Hesap Durumu")
    komisyonlar = models.ManyToManyField(Komisyon, blank=True, verbose_name="İlgili Olduğu Komisyonlar")
    ozel_notlar = models.TextField(blank=True, null=True, verbose_name="Yönetici Notları")

    def __str__(self):
        return self.user.username

class Duyuru(models.Model):
    baslik = models.CharField(max_length=200, verbose_name="Başlık")
    icerik = models.TextField(verbose_name="İçerik")
    yayin_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Yayın Tarihi")
    yazar = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Yazarı")
    class Meta:
        verbose_name = "Duyuru"
        verbose_name_plural = "Duyurular"
        ordering = ['-yayin_tarihi']
    def __str__(self):
        return self.baslik

class Etkinlik(models.Model):
    class EtkinlikTipi(models.TextChoices):
        SOHBET = 'SOHBET', 'Sohbet'
        KONFERANS = 'KONFERANS', 'Konferans'
        GEZI = 'GEZI', 'Gezi'
        SABAH_NAMAZI = 'SABAH_NAMAZI', 'Sabah Namazı'
        DIGER = 'DIGER', 'Diğer'
    baslik = models.CharField(max_length=200, verbose_name="Etkinlik Başlığı")
    tip = models.CharField(max_length=20, choices=EtkinlikTipi.choices, verbose_name="Etkinlik Tipi")
    aciklama = models.TextField(verbose_name="Açıklama")
    tarih_saat = models.DateTimeField(verbose_name="Tarih ve Saat")
    mekan = models.CharField(max_length=255, verbose_name="Mekan")
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
    class Meta:
        verbose_name = "Etkinlik"
        verbose_name_plural = "Etkinlikler"
        ordering = ['-tarih_saat']
    def __str__(self):
        return self.baslik

class Album(models.Model):
    baslik = models.CharField(max_length=200, verbose_name="Albüm Başlığı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    class Meta:
        verbose_name = "Albüm"
        verbose_name_plural = "Albümler"
        ordering = ['-olusturma_tarihi']
    def __str__(self):
        return self.baslik
    def kapak_fotografi(self):
        return self.fotograflar.order_by('yuklenme_tarihi').first()

class Fotograf(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='fotograflar', verbose_name="Ait Olduğu Albüm")
    resim = models.ImageField(upload_to='galeri/', verbose_name="Resim Dosyası")
    yuklenme_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Yüklenme Tarihi")
    class Meta:
        verbose_name = "Fotoğraf"
        verbose_name_plural = "Fotoğraflar"
        ordering = ['-yuklenme_tarihi']
    def __str__(self):
        return f"{self.album.baslik} - Fotoğraf {self.id}"

# ==========================================================
# ===== YENİ EKLENEN "KİŞİSEL NİZAM" NOT DEFTERİ MODELİ =====
# ==========================================================

class Not(models.Model):
    class RenkSecenekleri(models.TextChoices):
        GRI = 'GRI', 'Varsayılan'
        SARI = 'SARI', 'Hatırlatıcı'
        KIRMIZI = 'KIRMIZI', 'Acil'
        MAVI = 'MAVI', 'Fikir'
        YESIL = 'YESIL', 'Görev'

    # Bu ForeignKey, her notu bir kullanıcıya bağlar ve gizliliği garanti eder.
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notlar', verbose_name="Notun Sahibi")
    
    baslik = models.CharField(max_length=255, verbose_name="Not Başlığı")
    icerik = models.TextField(blank=True, null=True, verbose_name="Not İçeriği")
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")
    
    # Notları sabitlemek/yıldızlamak için.
    onemli_mi = models.BooleanField(default=False, verbose_name="Önemli Olarak İşaretle")
    
    # Notları renk kodlamak için.
    renk = models.CharField(max_length=10, choices=RenkSecenekleri.choices, default=RenkSecenekleri.GRI, verbose_name="Not Rengi")

    class Meta:
        verbose_name = "Kişisel Not"
        verbose_name_plural = "Kişisel Notlar"
        # Notları en son güncellenene göre sırala, önemliler her zaman en üstte olsun.
        ordering = ['-onemli_mi', '-guncelleme_tarihi']

    def __str__(self):
        return f"{self.kullanici.username} - {self.baslik}"
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    
    # --- DEĞİŞİKLİK BURADA ---
    # Bu alan artık hem e-posta hem de telefon numarası kabul edecek
    contact_info = models.CharField(max_length=255, verbose_name="E-posta veya Telefon Numarası")
    # -------------------------

    subject = models.CharField(max_length=200, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesajınız")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Zamanı")
    is_read = models.BooleanField(default=False, verbose_name="Okundu mu?")

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-timestamp']