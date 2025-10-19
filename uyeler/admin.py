from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# ===== DEĞİŞİKLİK BURADA: Artık 'Galeri' yerine 'Album' ve 'Fotograf' import ediyoruz =====
from .models import Komisyon, Profil, Duyuru, Etkinlik, Album, Fotograf

# --- User Admin Ayarları (SENİN KODUNLA AYNI, DOKUNULMADI) ---

# Django'nun varsayılan User adminini kaldırıyoruz
admin.site.unregister(User)

class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = 'Profil Bilgileri'
    fieldsets = (
        (None, {'fields': ('rol', 'statü', 'komisyonlar')}),
        ('Özel Bilgiler (Sadece Yetkili Görür)', {
            'classes': ('collapse',),
            'fields': ('ozel_notlar',),
        })
    )

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_profil_rol', 'get_profil_statu')
    list_select_related = ('profil',)
    
    @admin.display(description='Rol', ordering='profil__rol')
    def get_profil_rol(self, obj):
        return obj.profil.get_rol_display()
        
    @admin.display(description='Statü', ordering='profil__statu')
    def get_profil_statu(self, obj):
        return obj.profil.get_statü_display()

# --- Komisyon, Duyuru, Etkinlik Admin Ayarları (SENİN KODUNLA AYNI) ---

@admin.register(Komisyon)
class KomisyonAdmin(admin.ModelAdmin):
    list_display = ('ad', 'id')
    search_fields = ('ad',)

@admin.register(Duyuru)
class DuyuruAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yazar', 'yayin_tarihi')
    list_filter = ('yayin_tarihi', 'yazar')
    search_fields = ('baslik', 'icerik')

@admin.register(Etkinlik)
class EtkinlikAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'tip', 'tarih_saat', 'olusturan')
    list_filter = ('tip', 'tarih_saat')
    search_fields = ('baslik', 'aciklama', 'mekan')

# --- DEĞİŞİKLİK BURADA BAŞLIYOR ---

# 1. ESKİ 'GaleriAdmin' KALDIRILDI.
# @admin.register(Galeri) ... bu bölüm tamamen silindi.

# 2. YENİ ALBÜM VE FOTOĞRAF ADMİN AYARLARI EKLENDİ.

# Bir albümü düzenlerken, içine fotoğrafları doğrudan eklemek için (inline)
class FotografInline(admin.TabularInline):
    model = Fotograf
    extra = 3 # Varsayılan olarak 3 tane boş fotoğraf yükleme alanı gösterir
    verbose_name = "Bu Albüme Ait Fotoğraf"
    verbose_name_plural = "Bu Albüme Ait Fotoğraflar"

# Album adminini oluşturup, Fotograf'ları içine yerleştiriyoruz
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'olusturma_tarihi')
    search_fields = ('baslik', 'aciklama')
    inlines = [FotografInline] # Fotograf ekleme formunu albümün içine gömüyoruz