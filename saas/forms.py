from django import forms
from user.models import User
from saas.models import Company,Company_Address



class CompanyForm(forms.ModelForm):
    yetkiliAd = forms.CharField(max_length=100, required=True)
    yetkiliAd.widget.attrs.update({'class': 'form-control','placeholder':'Yetkili Ad '})
    yetkiliSoyad = forms.CharField(max_length=100, required=True)
    yetkiliSoyad.widget.attrs.update({'class': 'form-control','placeholder':'Yetkili Soyad'})
    yetkiliTelefon = forms.CharField(max_length=100, required=True)
    yetkiliTelefon.widget.attrs.update({'class': 'form-control','placeholder':'Yetkili Telefon'})
    yetkiliEmail = forms.CharField(max_length=100, required=True)
    yetkiliEmail.widget.attrs.update({'class': 'form-control','placeholder':'Yetkili Email'})

    class Meta:

        model = Company
        fields = ['name','yetkiliAd','yetkiliSoyad','yetkiliTelefon','yetkiliEmail','adres','telefon','email','web','logo','description']

class CompanyAddressForm(forms.ModelForm):

    class Meta:

        model = Company_Address
        fields = ['ulke','il','ilce','mahalle','adres','map_link','aciklama','active']




    