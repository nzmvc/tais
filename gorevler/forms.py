from re import VERBOSE
from django import forms
from .models import Gorevler,GorevNotu,GorevlerStatu,Reminder,ReminderType,GorevType,DuzenliGorevTanim
from user.models import User,Employee
from django.forms.widgets import DateInput
from django.core.exceptions import ValidationError
import datetime

class DuzenliGorevForm(forms.ModelForm):

        days_of_week = forms.MultipleChoiceField(
            choices=[
                (1, "Pazartesi"),
                (2, "Salı"),
                (3, "Çarşamba"),
                (4, "Perşembe"),
                (5, "Cuma"),
                (6, "Cumartesi"),
                (7, "Pazar"),
            ],
            widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_days_of_week'}),
            label="Haftanın Günleri",
            required=False,
        )
        
        days_of_month = forms.MultipleChoiceField(
            choices=[(i, f"{i}. Gün") for i in range(1, 32)],  # 1'den 31'e kadar günler
            widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_days_of_month'}),
            label="Ayın Günleri",
            required=False,
        )
        
        def __init__(self,c_id, *args, **kwargs):
            super(DuzenliGorevForm,self).__init__(*args, **kwargs)
            # Kullanıcıların yalnızca kendi şirketlerine ait kullanıcıları seçebilmesini sağlayın
            self.fields['responsible_user'].queryset = User.objects.filter(id__in = Employee.objects.values_list('user_id',flat=True).filter(company_id=c_id) )
            # Kullanıcıların tam adlarını birleştirerek döndürün
            self.fields['responsible_user'].label_from_instance = self.get_full_name
    
        def get_full_name(self, obj):
            # Kullanıcının tam adını birleştirerek döndürün
            return f"{obj.first_name} {obj.last_name}"
        
        class Meta:
    
            model = DuzenliGorevTanim
            fields = ['title','description','start_date','end_date','repeat_type','frequency','days_of_week','days_of_month','numberOfDayOpen','numberOfDayCreate','department','responsible_user','document']
            widgets = {
                'repeat_type': forms.Select(attrs={'id': 'id_repeat_type'}),
                'start_date': DateInput(attrs={'type': 'date'}),
                'end_date': DateInput(attrs={'type': 'date'}),
                'title': forms.TextInput(attrs={'placeholder': 'Örnek: Çöp kutularının boşaltılması'}),
                'description': forms.Textarea(attrs={'placeholder': 'Örnek: Çöp kutularının boşaltılması ve çöplerin çıkartılması'}),
            }

            def clean(self):
                cleaned_data = super().clean()
                start_date = cleaned_data.get("start_date")
                end_date = cleaned_data.get("end_date")
    
                if start_date and end_date and start_date > end_date:
                    # hata mesajı döndür
                    raise ValidationError("Başlangıç tarihi, bitiş tarihinden büyük olamaz.")
                return cleaned_data
            
class GorevForm(forms.ModelForm):

    smsGonder = forms.ChoiceField(choices=[(True, 'Evet'), (False, 'Hayır')],label="Whatsapp - SMS Bilgilendirme Gönder")
    
    def __init__(self,c_id, *args, **kwargs):
        super(GorevForm,self).__init__(*args, **kwargs)
        # Kullanıcıların yalnızca kendi şirketlerine ait kullanıcıları seçebilmesini sağlayın
        self.fields['responsible_user'].queryset = User.objects.filter(id__in = Employee.objects.values_list('user_id',flat=True).filter(company_id=c_id) )
        # Kullanıcıların tam adlarını birleştirerek döndürün
        self.fields['responsible_user'].label_from_instance = self.get_full_name

    def get_full_name(self, obj):
        # Kullanıcının tam adını birleştirerek döndürün
        return f"{obj.first_name} {obj.last_name}"
    
    class Meta:

        model = Gorevler
        fields = ['responsible_user','title','description','dokuman','start_date','deadline']
        widgets = {
            'deadline': DateInput(attrs={'type': 'datetime-local'}),
            'start_date': DateInput(attrs={'type': 'datetime-local'}),
            'title': forms.TextInput(attrs={'placeholder': 'Kısa açıklama'}),
        }

        # formu gonderirken clean metodu ile verileri kontrol edebiliriz
        # burada start_date ve deadline alanlarını kontrol ediyoruz. Eğer start_date > deadline ise hata mesajı döndürüyoruz.
        def clean(self):
            cleaned_data = super().clean()
            start_date = cleaned_data.get("start_date")
            deadline = cleaned_data.get("deadline")

            if start_date and deadline and start_date > deadline:
                # hata mesajı döndür
                raise ValidationError("Başlangıç tarihi, bitiş tarihinden büyük olamaz.")
            if deadline < datetime.datetime.now():
                raise ValidationError("Bitiş tarihi bugünden küçük olamaz.")
            return cleaned_data

class GorevIlkForm(forms.ModelForm):

    class Meta:

        model = Gorevler
        fields = ['title','description','dokuman','start_date','deadline']
        widgets = {
            'deadline': DateInput(attrs={'type': 'datetime-local'}),
            'start_date': DateInput(attrs={'type': 'datetime-local'}),
            'title': forms.TextInput(attrs={'placeholder': 'Örnek: Ali Bey’in kargosu gönderilecek'}),
            #'description = attrs={'placeholder': 'Örnek: Ali Bey’in paketi kargoya verilmeli ve kendisi aranarak bilgilendirilmeli'}
            'description': forms.Textarea(attrs={'placeholder': 'Örnek: Ali Bey’in paketi kargoya verilmeli ve kendisi aranarak bilgilendirilmeli'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        deadline = cleaned_data.get("deadline")

        if start_date and deadline and start_date > deadline:
            raise ValidationError("Başlangıç tarihi, bitiş tarihinden büyük olamaz.")
        if deadline < datetime.datetime.now():
            raise ValidationError("Bitiş tarihi bugünden küçük olamaz.")
        return cleaned_data

class GorevNotuForm(forms.ModelForm):

    class Meta:

        model = GorevNotu
        fields = ['description','dokuman']

class GorevTamamla(forms.ModelForm):
    class Meta:
        model = Gorevler
        fields = ['solution','harcama']

class GorevStatuForm(forms.ModelForm):
    class Meta:
        model = GorevlerStatu
        fields = ['statu','aciklama']

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['time','time_type','type','reminder_date','description']
        widgets = {
            'reminder_date': DateInput(attrs={'type': 'datetime-local'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        reminder_date = cleaned_data.get("reminder_date")
        if reminder_date:
            if reminder_date < datetime.datetime.now():
                raise ValidationError("Hatırlatma tarihi bugünden küçük olamaz.")
        return cleaned_data
    