# uyeler/urls.py

from django.urls import path
from . import views

app_name = 'uyeler'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('uyeler/', views.uyeler_view, name='uyeler'),
    path('gundem/', views.gundem_view, name='gundem'),
    path('gundem/duyuru-ekle/', views.duyuru_ekle_view, name='duyuru_ekle'),
    path('gundem/etkinlik-ekle/', views.etkinlik_ekle_view, name='etkinlik_ekle'),
    path('gundem/duyuru/<int:pk>/duzenle/', views.duyuru_duzenle_view, name='duyuru_duzenle'),
    path('gundem/duyuru/<int:pk>/sil/', views.duyuru_sil_view, name='duyuru_sil'),
    path('gundem/etkinlik/<int:pk>/duzenle/', views.etkinlik_duzenle_view, name='etkinlik_duzenle'),
    path('gundem/etkinlik/<int:pk>/sil/', views.etkinlik_sil_view, name='etkinlik_sil'),
    
    # YENİ EKLENEN SATIR: Galeri sayfasının URL'si.
    # Hem albümleri listelemek (GET) hem de yeni albüm eklemek (POST) için bu URL kullanılacak.
    path('galeri/', views.galeri_view, name='galeri'),
    path('galeri/<int:album_id>/', views.album_detay_view, name='album_detay'),
    path('galeri/ekle/', views.album_ekle_view, name='album_ekle'),
    path('galeri/<int:album_id>/fotograf-ekle/', views.album_fotograf_ekle_view, name='album_fotograf_ekle'),
    # Kullanıcı onay ve rol atama işlemleri için URL'ler
    path('uyeler/onayla/<int:user_id>/', views.kullanici_onayla_view, name='kullanici_onayla'),
    path('uyeler/reddet/<int:user_id>/', views.kullanici_reddet_view, name='kullanici_reddet'),
    # Albüm başlığını/açıklamasını düzenleme sayfası
    path('galeri/<int:album_id>/duzenle/', views.album_duzenle_view, name='album_duzenle'),
    # Belirli bir fotoğrafı silme işlemi
    path('galeri/fotograf/<int:fotograf_id>/sil/', views.fotograf_sil_view, name='fotograf_sil'),
    path('galeri/<int:album_id>/sil/', views.album_sil_view, name='album_sil'),
    # /not-defteri/ -> Ana not defteri sayfasını açar
    path('not-defteri/', views.not_defteri_view, name='not_defteri'),
    # /not-defteri/5/ -> 5 numaralı notu seçili olarak açar
    path('not-defteri/<int:not_id>/', views.not_defteri_view, name='not_defteri'),
    # /not-defteri/5/sil/ -> 5 numaralı notu siler
    path('not-defteri/<int:not_id>/sil/', views.not_sil_view, name='not_sil'),
    path('uyeler/rol-duzenle/<int:user_id>/', views.kullanici_rol_duzenle_view, name='kullanici_rol_duzenle'),
    path('galeri/<int:album_id>/indir/', views.album_indir_view, name='album_indir'),
    path("aktif-et/", views.aktif_et),
]