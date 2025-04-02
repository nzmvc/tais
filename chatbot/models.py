# models.py
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
from user.models import User
from saas.models import Company


def user_chatbot_directory_path(instance, filename):
    return f'user_{instance.chatbot.user.id}/chatbot_{instance.chatbot.id}/{filename}'

class Chatbot(models.Model):
    #TODO: https://platform.openai.com/docs/api-reference/assistants/createAssistant sayfasını inncele eklenebilecek birçok özellik var.
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbots')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # OpenAI related fields
    assistant_id = models.CharField(max_length=255, blank=True, null=True)
    vector_store_id = models.CharField(max_length=255, blank=True, null=True)
    instructions = models.TextField(
        default="Sen destek asistanısın. Kullanıcıların sorularını enfazla 4 cümlede yanıtlayacaksın. Soru dili ne ise o dilde cevap ver. Eğer sorunun cevabını bilmiyorsan, kullanıcıyı bir telefona veya mail adresine yönlendir.",
        help_text="Destek konusunu belirtin. cevaplama şeklini veya kısıtları söyleyebilirsiniz. bilmediği konularda bir telefona veya mail adresine yönlendirme yapılabilir."
    )
    
    # Configuration
    model = models.CharField(
        max_length=50,
        default="gpt-4-1106-preview",
        choices=[("gpt-4-1106-preview", "GPT-4"), ("gpt-3.5-turbo", "GPT-3.5")]
    )
    temperature = models.FloatField(default=0.7,
                                    help_text="Sıcaklık değeri. 0.0 ile 1.0 arasında olmalıdır. 0.0  daha net cevaplar fakat az yaratıcılık, 1.0 en fazla üretken konunun özeünnden uzaklaşmasına sebep olabilir")
    
    #TODO: openia da birden fazla model var. bunları ekleyip, kullanıcıya seçtirebiliriz.
    """
    tools = models.CharField(
        max_length=255,
        default="browser,code interpreter",
        choices=[("gpt-4-1106-preview", "GPT-4"), ("gpt-3.5-turbo", "GPT-3.5")
    )"""
    
    # Embedding
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    widget_color = models.CharField(max_length=7, default='#3B82F6', help_text="Chatbot widget rengi. Hex kodu olarak girin.")
    """widget_position = models.CharField(
        max_length=10,
        default='right',
        choices=[('left', 'Left'), ('right', 'Right')],
        help_text="Chatbot widget konumu. Sol veya sağ olarak ayarlayın."
    )
    widget_text_color = models.CharField(max_length=7, default='#FFFFFF', help_text="Chatbot widget yazı rengi. Hex kodu olarak girin.")
    """
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.name}"

class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(
        upload_to=user_chatbot_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'md', 'docx', 'csv'])]
    )
    
    vector_id = models.CharField(max_length=255, blank=True)
    
    PROCESSING_STATUS = (
        ('P', 'Processing'),
        ('S', 'Success'),
        ('F', 'Failed')
    )
    status = models.CharField(max_length=1, choices=PROCESSING_STATUS, default='P')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_user = models.ForeignKey(User, verbose_name="Kaydı Açan",null=True,blank=True,on_delete=models.SET_NULL)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,null=True,blank=True,)
    
    #TODO: dosya boyutunu da tutabiliriz
    #size = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.file.name} ({self.get_status_display()})"

class ChatbotSession(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='sessions')
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['session_id'])]

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatbotSession, on_delete=models.CASCADE, related_name='messages')
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System')
    ]
    role = models.CharField(max_length=9, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"