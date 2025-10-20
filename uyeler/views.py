# uyeler/views.py (TÜM MODÜLLERİYLE TAM VE ÇALIŞAN NİHAİ SÜRÜM)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import Profil, Duyuru, Etkinlik, Album, Fotograf, Not, ContactMessage
from itertools import chain
from .forms import ContactForm
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @login_required(login_url='uyeler:login')
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.profil.rol in allowed_roles:
                messages.error(request, "Bu sayfayı görüntüleme yetkiniz bulunmamaktadır.")
                return redirect('uyeler:home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# --- ANA SAYFA VE GÜNDEM VIEW'LARI ---
def home_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid() and not form.cleaned_data.get('honeypot'):
            contact_message = form.save()
            try:
                reply_to_list = []
                if '@' in contact_message.contact_info:
                    reply_to_list.append(contact_message.contact_info)

                subject = f"AGD Şişli Sitesinden Yeni Mesaj: {contact_message.subject}"
                message_body = f"""
                Gönderen: {contact_message.name}
                İletişim Bilgisi: {contact_message.contact_info}
                Konu: {contact_message.subject}
                --------------------------------------------------
                Mesaj: {contact_message.message}
                """

                email = EmailMessage(
                    subject=subject,
                    body=message_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=['sislianadolugenclik@gmail.com'],
                    reply_to=reply_to_list
                )
                email.send()
                messages.success(request, 'Mesajınız başarıyla gönderildi. Teşekkür ederiz!')

            except Exception as e:
                print(f"E-POSTA GÖNDERİM HATASI (NİHAİ KOD): {e}")
                messages.warning(request, 'Mesajınız kaydedildi ancak e-posta gönderiminde bir sorun yaşandı.')
            
            return redirect('/#contact')
        else:
            messages.success(request, 'Mesajınız başarıyla gönderildi. Teşekkür ederiz!')
            return redirect('/#contact')
    else:
        form = ContactForm()

    context = {}
    if request.user.is_authenticated:
        try:
            profil = request.user.profil
            onay_bekleyenler_sayisi = 0
            if profil.rol == 'YETKILI':
                onay_bekleyenler_sayisi = Profil.objects.filter(statü='BEKLEMEDE').count()
            context.update({'profil': profil, 'onay_bekleyenler_sayisi': onay_bekleyenler_sayisi})
        except Profil.DoesNotExist:
            context.update({'profil': None})

    # 🩵 HATA DÜZELTİLEN KISIM 🩵
    son_duyurular = Duyuru.objects.order_by('-yayin_tarihi')[:3]
    son_etkinlikler = Etkinlik.objects.order_by('-tarih_saat')[:3]

    # Her iki modelin de tarih alanı farklı olduğundan, güvenli karşılaştırma yapıyoruz
    def get_tarih(obj):
        if hasattr(obj, 'yayin_tarihi'):
            return obj.yayin_tarihi
        elif hasattr(obj, 'tarih_saat'):
            return obj.tarih_saat
        return None

    gundem_listesi = sorted(chain(son_duyurular, son_etkinlikler), key=get_tarih, reverse=True)

    son_galeri_resimleri = Fotograf.objects.order_by('-yuklenme_tarihi')

    context.update({
        'gundem_listesi': gundem_listesi,
        'son_galeri_resimleri': son_galeri_resimleri,
        'form': form
    })

    return render(request, 'uyeler/home.html', context)


def gundem_view(request):
    tum_duyurular = Duyuru.objects.all()
    tum_etkinlikler = Etkinlik.objects.all()
    context = {'duyurular': tum_duyurular, 'etkinlikler': tum_etkinlikler}
    return render(request, 'uyeler/gundem.html', context)


# ------------------------------
# GALERİ
# ------------------------------
def galeri_view(request):
    if request.method == 'POST':
        if request.user.profil.rol in ['YETKILI', 'BIRIM_BASKANI']:
            baslik = request.POST.get('baslik')
            aciklama = request.POST.get('aciklama')
            if baslik:
                yeni_album = Album.objects.create(baslik=baslik, aciklama=aciklama, olusturan=request.user)
                messages.success(request, f'"{yeni_album.baslik}" başlıklı albüm başarıyla oluşturuldu. Şimdi fotoğrafları ekleyebilirsiniz.')
                return redirect('uyeler:album_fotograf_ekle', album_id=yeni_album.id)
            else:
                messages.error(request, 'Albüm başlığı boş bırakılamaz.')
        else:
            messages.error(request, 'Bu işlemi yapmak için yetkiniz bulunmamaktadır.')
        return redirect('uyeler:galeri')

    albumler = Album.objects.all()
    context = {'albumler': albumler}
    return render(request, 'uyeler/galeri.html', context)

@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def album_ekle_view(request):
    if request.method == 'POST':
        baslik = request.POST.get('baslik')
        aciklama = request.POST.get('aciklama')
        if baslik:
            yeni_album = Album.objects.create(baslik=baslik, aciklama=aciklama, olusturan=request.user)
            messages.success(request, f'"{yeni_album.baslik}" başlıklı albüm başarıyla oluşturuldu. Şimdi fotoğrafları ekleyebilirsiniz.')
            
            # ===== DEĞİŞİKLİK BURADA: Artık admin paneline değil, yeni fotoğraf ekleme sayfamıza yönlendiriyoruz =====
            return redirect('uyeler:album_fotograf_ekle', album_id=yeni_album.id)
            # ===================================================================================================
            
        else:
            messages.error(request, 'Albüm başlığı boş bırakılamaz.')
            return render(request, 'uyeler/album_ekle.html')
            
    # Sayfa ilk açıldığında boş formu göster.
    return render(request, 'uyeler/album_ekle.html')

@login_required(login_url='uyeler:login')
@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def album_fotograf_ekle_view(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    
    # Eğer form gönderilmişse...
    if request.method == 'POST':
        # formdan gelen tüm resimleri 'resimler' listesine al
        resimler = request.FILES.getlist('resimler')
        
        if not resimler:
            messages.warning(request, "Lütfen en az bir fotoğraf seçin.")
        else:
            for resim in resimler:
                Fotograf.objects.create(album=album, resim=resim)
            messages.success(request, f'{len(resimler)} adet fotoğraf başarıyla "{album.baslik}" albümüne eklendi.')
            # İşlem bittikten sonra albümün detay sayfasına yönlendir
            return redirect('uyeler:album_detay', album_id=album.id)
            
    # Sayfa ilk açıldığında veya hata durumunda formu göster
    context = {'album': album}
    return render(request, 'uyeler/album_fotograf_ekle.html', context)

@login_required(login_url='uyeler:login')
def album_detay_view(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    fotograflar = album.fotograflar.all()
    context = {'album': album, 'fotograflar': fotograflar}
    return render(request, 'uyeler/album_detay.html', context)

@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def album_duzenle_view(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    
    if request.method == 'POST':
        yeni_baslik = request.POST.get('baslik')
        yeni_aciklama = request.POST.get('aciklama')
        
        if yeni_baslik:
            album.baslik = yeni_baslik
            album.aciklama = yeni_aciklama
            album.save()
            messages.success(request, 'Albüm bilgileri başarıyla güncellendi.')
            return redirect('uyeler:album_detay', album_id=album.id)
        else:
            messages.error(request, 'Albüm başlığı boş bırakılamaz.')

    context = {'album': album}
    return render(request, 'uyeler/album_duzenle.html', context)


# ===== YENİ FOTOĞRAF SİLME FONKSİYONU =====
@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def fotograf_sil_view(request, fotograf_id):
    fotograf = get_object_or_404(Fotograf, id=fotograf_id)
    album_id = fotograf.album.id  # Yönlendirme için albüm ID'sini sakla

    if request.method == 'POST':
        fotograf.delete()
        messages.success(request, 'Fotoğraf başarıyla silindi.')
        return redirect('uyeler:album_detay', album_id=album_id)

    # GET isteği için onay sayfası göster
    context = {'fotograf': fotograf}
    return render(request, 'uyeler/fotograf_sil_onay.html', context)

# --- KULLANICI YÖNETİMİ VIEW'LARI ---
@role_required(allowed_roles=['YETKILI'])

@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def album_sil_view(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    # Eğer kullanıcı "Evet, Sil" butonuna basmışsa (POST isteği)...
    if request.method == 'POST':
        album.delete()
        messages.success(request, f'"{album.baslik}" başlıklı albüm ve içindeki tüm fotoğraflar kalıcı olarak silindi.')
        # İşlem bittikten sonra ana galeri sayfasına yönlendir
        return redirect('uyeler:galeri')

    # Sayfa ilk açıldığında (GET isteği), onay sayfasını göster
    context = {'album': album}
    return render(request, 'uyeler/album_sil_onay.html', context)

@login_required(login_url='uyeler:login')
def album_indir_view(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    fotograflar = album.fotograflar.all()

    # Eğer albümde fotoğraf yoksa, hata mesajıyla geri yönlendir
    if not fotograflar:
        messages.warning(request, f'"{album.baslik}" albümünde indirilecek fotoğraf bulunmamaktadır.')
        return redirect('uyeler:album_detay', album_id=album.id)

    # Bellekte geçici bir dosya oluştur
    buffer = io.BytesIO()

    # Bu geçici dosyayı bir ZIP dosyası olarak kullan
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for fotograf in fotograflar:
            # Her fotoğrafı diskten oku ve ZIP dosyasına ekle
            # 'arcname' kullanarak dosyanın tam yolunu değil, sadece adını ZIP'e yazıyoruz
            zip_file.write(fotograf.resim.path, arcname=fotograf.resim.name.split('/')[-1])

    # HTTP cevabını hazırla
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    
    # İndirilecek dosya için güvenli bir isim oluştur (örn: 2024-yaz-kampi.zip)
    filename = f"{slugify(album.baslik)}.zip"
    
    # Tarayıcıya bu cevabın bir indirme dosyası olduğunu söyle
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

@role_required(allowed_roles=['YETKILI'])
def uyeler_view(request):
    onay_bekleyen_kullanicilar = Profil.objects.filter(statü='BEKLEMEDE').select_related('user')
    aktif_kullanicilar = Profil.objects.filter(statü='AKTIF').select_related('user')
    context = {'onay_bekleyenler': onay_bekleyen_kullanicilar, 'aktif_kullanicilar': aktif_kullanicilar, 'profil': request.user.profil} # profil eklendi
    return render(request, 'uyeler/uyeler.html', context)

@role_required(allowed_roles=['YETKILI'])
def kullanici_onayla_view(request, user_id):
    if request.method == 'POST':
        try:
            profil_to_update = Profil.objects.get(user_id=user_id)
            yeni_rol = request.POST.get('rol')
            if yeni_rol in Profil.Rol.values:
                profil_to_update.rol = yeni_rol
                profil_to_update.statü = Profil.Status.AKTIF
                profil_to_update.save()
                messages.success(request, f"{profil_to_update.user.username} adlı kullanıcının rolü '{profil_to_update.get_rol_display()}' olarak atandı ve hesabı aktifleştirildi.")
            else:
                messages.error(request, "Geçersiz bir rol seçildi.")
        except Profil.DoesNotExist:
            messages.error(request, "İşlem yapılmak istenen kullanıcı bulunamadı.")
    return redirect('uyeler:uyeler')

@role_required(allowed_roles=['YETKILI'])
def kullanici_reddet_view(request, user_id):
    try:
        profil_to_update = Profil.objects.get(user_id=user_id)
        profil_to_update.statü = Profil.Status.REDDEDILDI
        profil_to_update.save()
        messages.warning(request, f"{profil_to_update.user.username} adlı kullanıcının başvurusu reddedildi.")
    except Profil.DoesNotExist:
        messages.error(request, "İşlem yapılmak istenen kullanıcı bulunamadı.")
    return redirect('uyeler:uyeler')

# --- GİRİŞ / KAYIT / ÇIKIŞ VIEW'LARI ---
def login_view(request):
    if request.user.is_authenticated: return redirect('uyeler:home')
    if request.method == 'POST':
        kullanici_adi = request.POST.get('username'); sifre = request.POST.get('password')
        user = authenticate(request, username=kullanici_adi, password=sifre)
        if user is not None:
            try:
                if hasattr(user, 'profil') and user.profil.statü == 'AKTIF':
                    login(request, user); return redirect('uyeler:home')
                elif hasattr(user, 'profil') and user.profil.statü == 'BEKLEMEDE':
                    messages.warning(request, 'Hesabınız henüz yönetici onayı beklemektedir.')
                else: messages.error(request, 'Hesabınız reddedilmiş veya aktif değil.')
            except Profil.DoesNotExist: messages.error(request, 'Profiliniz bulunamadı.')
        else: messages.error(request, 'Hatalı kullanıcı adı veya şifre.')
    return render(request, 'uyeler/login.html')

def logout_view(request):
    logout(request); messages.info(request, "Başarıyla çıkış yaptınız."); return redirect('uyeler:login')

def register_view(request):
    if request.user.is_authenticated: return redirect('uyeler:home')
    if request.method == 'POST':
        ad = request.POST.get('first_name'); soyad = request.POST.get('last_name')
        kullanici_adi = request.POST.get('username'); email = request.POST.get('email'); sifre = request.POST.get('password')
        if User.objects.filter(username=kullanici_adi).exists(): messages.error(request, "Bu kullanıcı adı zaten alınmış.")
        elif User.objects.filter(email=email).exists(): messages.error(request, "Bu e-posta adresi zaten kullanılıyor.")
        else:
            yeni_kullanici = User.objects.create_user(username=kullanici_adi, email=email, password=sifre)
            yeni_kullanici.first_name = ad; yeni_kullanici.last_name = soyad; yeni_kullanici.save()
            Profil.objects.create(user=yeni_kullanici)
            messages.success(request, 'Kaydınız başarıyla oluşturuldu. Yönetici onayından sonra giriş yapabilirsiniz.')
            return redirect('uyeler:login')
    return render(request, 'uyeler/register.html')

# --- DUYURU VE ETKİNLİK YÖNETİM (CRUD) VIEW'LARI ---
@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def duyuru_ekle_view(request):
    if request.method == 'POST':
        baslik = request.POST.get('baslik'); icerik = request.POST.get('icerik')
        if baslik and icerik:
            Duyuru.objects.create(baslik=baslik, icerik=icerik, yazar=request.user)
            messages.success(request, "Duyuru başarıyla eklendi."); return redirect('uyeler:gundem')
    return render(request, 'uyeler/duyuru_ekle.html')

@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def duyuru_duzenle_view(request, pk):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    if request.method == 'POST':
        duyuru.baslik = request.POST.get('baslik'); duyuru.icerik = request.POST.get('icerik')
        duyuru.save(); messages.success(request, "Duyuru başarıyla güncellendi."); return redirect('uyeler:gundem')
    return render(request, 'uyeler/duyuru_duzenle.html', {'duyuru': duyuru})

@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def duyuru_sil_view(request, pk):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    if request.method == 'POST':
        duyuru.delete(); messages.success(request, "Duyuru başarıyla silindi."); return redirect('uyeler:gundem')
    return render(request, 'uyeler/duyuru_sil.html', {'nesne': duyuru})

@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def etkinlik_ekle_view(request):
    if request.method == 'POST':
        # ... (POST işlemleri aynı kalıyor)
        tip = request.POST.get('tip'); aciklama = request.POST.get('aciklama'); tarih_saat = request.POST.get('tarih_saat'); mekan = request.POST.get('mekan')
        baslik = f"{dict(Etkinlik.EtkinlikTipi.choices)[tip]} Buluşması" if tip == 'SABAH_NAMAZI' else request.POST.get('baslik')
        Etkinlik.objects.create(baslik=baslik, tip=tip, aciklama=aciklama, tarih_saat=tarih_saat, mekan=mekan, olusturan=request.user)
        messages.success(request, "Etkinlik başarıyla eklendi."); return redirect('uyeler:gundem')
    
    # ===== DEĞİŞİKLİK BURADA =====
    # Etkinlik tiplerini (Sohbet, Gezi vb.) şablona gönderiyoruz.
    context = {
        'etkinlik_tipleri': Etkinlik.EtkinlikTipi.choices
    }
    return render(request, 'uyeler/etkinlik_ekle.html', context)

@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def etkinlik_duzenle_view(request, pk):
    etkinlik = get_object_or_404(Etkinlik, pk=pk)
    if request.method == 'POST':
        # ... (POST işlemleri aynı kalıyor)
        etkinlik.baslik = request.POST.get('baslik'); etkinlik.tip = request.POST.get('tip'); etkinlik.aciklama = request.POST.get('aciklama')
        etkinlik.tarih_saat = request.POST.get('tarih_saat'); etkinlik.mekan = request.POST.get('mekan')
        etkinlik.save(); messages.success(request, "Etkinlik başarıyla güncellendi."); return redirect('uyeler:gundem')
    
    # ===== DEĞİŞİKLİK BURADA =====
    # Hem düzenlenecek etkinliği hem de tüm etkinlik tiplerini şablona gönderiyoruz.
    context = {
        'etkinlik': etkinlik,
        'etkinlik_tipleri': Etkinlik.EtkinlikTipi.choices
    }
    return render(request, 'uyeler/etkinlik_duzenle.html', context)
@role_required(allowed_roles=['YETKILI', 'BIRIM_BASKANI'])
def etkinlik_sil_view(request, pk):
    etkinlik = get_object_or_404(Etkinlik, pk=pk)
    if request.method == 'POST':
        etkinlik.delete(); messages.success(request, "Etkinlik başarıyla silindi."); return redirect('uyeler:gundem')
    return render(request, 'uyeler/etkinlik_sil.html', {'nesne': etkinlik})

@login_required(login_url='uyeler:login')
def not_defteri_view(request, not_id=None):
    tum_notlar = Not.objects.filter(kullanici=request.user)
    aktif_not = None
    
    # ===== DEĞİŞİKLİK BURADA: POST METODU TAMAMEN YENİDEN YAZILDI =====
    if request.method == 'POST':
        not_id_form = request.POST.get('not_id')
        baslik = request.POST.get('baslik')
        icerik = request.POST.get('icerik')

        if not baslik:
            messages.error(request, "Not başlığı boş bırakılamaz.")
            return redirect('uyeler:not_defteri')
        
        # Eğer gizli not_id alanı doluysa, bu bir DÜZENLEME işlemidir.
        if not_id_form:
            guncellenecek_not = get_object_or_404(Not, id=not_id_form, kullanici=request.user)
            guncellenecek_not.baslik = baslik
            guncellenecek_not.icerik = icerik
            guncellenecek_not.save()
            messages.success(request, f'"{baslik}" başlıklı not başarıyla güncellendi.')
            return redirect('uyeler:not_defteri', not_id=guncellenecek_not.id)
        # Eğer not_id boşsa, bu YENİ BİR NOT oluşturma işlemidir.
        else:
            yeni_not = Not.objects.create(kullanici=request.user, baslik=baslik, icerik=icerik)
            messages.success(request, f'"{baslik}" başlıklı yeni not başarıyla oluşturuldu.')
            return redirect('uyeler:not_defteri', not_id=yeni_not.id)

    if not_id:
        aktif_not = get_object_or_404(Not, id=not_id, kullanici=request.user)
    
    context = {'tum_notlar': tum_notlar, 'aktif_not': aktif_not}
    return render(request, 'uyeler/not_defteri.html', context)

@login_required(login_url='uyeler:login')
def not_sil_view(request, not_id):
    silinecek_not = get_object_or_404(Not, id=not_id, kullanici=request.user)
    if request.method == 'POST':
        silinecek_not.delete()
        messages.success(request, 'Not kalıcı olarak silindi.')
        return redirect('uyeler:not_defteri')
    return render(request, 'uyeler/not_sil_onay.html', {'not': silinecek_not})

@role_required(allowed_roles=['YETKILI'])
def kullanici_rol_duzenle_view(request, user_id):
    # Düzenlenecek profili bul, yoksa 404 hatası ver
    profil_duzenle = get_object_or_404(Profil, user_id=user_id)

    # Eğer form gönderilmişse (POST isteği)...
    if request.method == 'POST':
        yeni_rol = request.POST.get('rol')
        if yeni_rol in Profil.Rol.values:
            profil_duzenle.rol = yeni_rol
            profil_duzenle.save()
            messages.success(request, f"'{profil_duzenle.user.username}' kullanıcısının rolü başarıyla güncellendi.")
            return redirect('uyeler:uyeler') # İşlem bitince üye listesine geri dön
        else:
            messages.error(request, "Geçersiz bir rol seçildi.")

    # Sayfa ilk açıldığında (GET isteği), formu göster
    context = {'profil_duzenle': profil_duzenle}
    return render(request, 'uyeler/rol_duzenle.html', context)