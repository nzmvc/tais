# forms.py
from django import forms
from django.core.validators import FileExtensionValidator
from .models import Chatbot, UploadedFile, ChatbotSession
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

#chatgpt form
class ChatbotForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        #widget=forms.FileInput(attrs={'multiple': True}),
        #widget=forms.ClearableFileInput(attrs={'multiple': True}),
        help_text="Chatbot'un eğitileceği dosyaları yükleyin (PDF, TXT, MD, DOCX, CSV)."
    )


    class Meta:
        model = Chatbot
        fields = ['name', 'description',"instructions", 'model', 'temperature', 'widget_color']

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        

#deepseek form
class ChatbotCreationForm(forms.ModelForm):
    files = forms.FileField(
        required=False,
        #widget=forms.ClearableFileInput(attrs={'multiple': True}),
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'md', 'docx', 'csv']),
            # Ek dosya validasyonları (opsiyonel)
            # MaxFileSizeValidator(max_size=1024*1024*5)  # 5MB limit
        ],
        label='Bilgi Dosyaları',
        help_text='PDF, TXT, DOCX ve CSV dosyaları yükleyebilirsiniz (Maks. 5MB/dosya)'
    )

    class Meta:
        model = Chatbot
        fields = [
            'name', 
            'description',
            'instructions',
            'model',
            'temperature',
            'widget_color'
        ]
        widgets = {
            'instructions': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Örnek: "Kullanıcılara profesyonel ve dostane bir dille cevap verin. Eğer bir soruyu cevaplayamıyorsanız, konuyu ilgili birime yönlendirin."'
            }),
            'description': forms.Textarea(attrs={'rows': 2}),
            'temperature': forms.NumberInput(attrs={
                'min': 0.0,
                'max': 1.0,
                'step': 0.1
            }),
            'widget_color': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'model': 'AI Modeli',
            'temperature': 'Yaratıcılık Seviyesi',
            'widget_color': 'Chatbot Rengi'
        }
        help_texts = {
            'temperature': '0 = Kesin Cevaplar, 1 = Yaratıcı Cevaplar',
            'model': 'Kullanılacak OpenAI model versiyonu'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

    def clean_files(self):
        files = self.files.getlist('files')
        if len(files) > 10:
            raise forms.ValidationError("Maksimum 10 dosya yükleyebilirsiniz")
        return files

    def save(self, commit=True):
        chatbot = super().save(commit=False)
        chatbot.user = self.user
        
        if commit:
            chatbot.save()
            
            # Dosya yükleme işlemi
            files = self.cleaned_data.get('files')
            if files:
                for file in files:
                    uploaded_file = UploadedFile(
                        chatbot=chatbot,
                        file=file,
                        created_user=self.user,
                        company=self.company
                    )
                    uploaded_file.save()
                    
                    # OpenAI'ye dosya yükleme işlemi (async olarak yapılmalı)
                    self.process_file_with_openai(uploaded_file)

            # Otomatik test işlemi
            self.run_initial_test(chatbot)
            
        return chatbot

    def process_file_with_openai(self, uploaded_file):
        # Bu kısımda OpenAI API entegrasyonu yapılacak
        # Örnek flow:
        # 1. Dosyayı OpenAI'ye yükle
        # 2. Vector Store ID'yi kaydet
        # 3. Assistant'ı güncelle
        # 4. Durumu güncelle
        try:
            # Mock implementation
            uploaded_file.status = 'S'
            uploaded_file.processed_at = timezone.now()
            uploaded_file.save()
        except Exception as e:
            uploaded_file.status = 'F'
            uploaded_file.save()
            # Hata loglama

    def run_initial_test(self, chatbot):
        # Basit bir test sorgusu ile chatbot kontrolü
        try:
            test_question = "Seni başarıyla oluşturabildim mi?"
            
            # Burada OpenAI API'si ile gerçek sorgu yapılacak
            mock_response = "Evet, başarıyla oluşturuldum! Nasıl yardımcı olabilirim?"
            
            # Test sonucunu loglama (opsiyonel)
            ChatbotSession.objects.create(
                chatbot=chatbot,
                ip_address='127.0.0.1',
                user_agent='System Test'
            )
        except Exception as e:
            # Hata durumunda işlemler
            chatbot.is_active = False
            chatbot.save()