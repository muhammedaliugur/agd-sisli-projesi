# uyeler/forms.py (Yeni oluşturduğun dosya)

from django import forms
from .models import ContactMessage # ContactMessage modelini import ediyoruz

from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    # Botları yakalamak için gizli bir tuzak alanı ekliyoruz.
    # Normal kullanıcılar bu alanı görmeyecek ve boş bırakacak.
    # Botlar ise körü körüne dolduracağı için tuzağa düşecek.
    honeypot = forms.CharField(
        required=False, 
        widget=forms.HiddenInput, 
        label="Bu alanı boş bırakın"
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'contact_info', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adınız ve Soyadınız',
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-posta veya Telefon',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mesajın Konusu',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mesajınızı buraya yazın...',
                'rows': 5,
            }),
        }