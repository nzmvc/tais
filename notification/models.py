from django.db import models
from user.models import User,Departments
from ckeditor.fields import RichTextField
from django.utils import timezone
from saas.models import Company

# Create your models here.


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='sender_notification')
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)

class ReadFlag(models.Model):
    id = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_notification')
    message = models.ForeignKey(Notification,on_delete=models.CASCADE,verbose_name="Mesaj")
    read_date = models.DateTimeField(verbose_name="Okunma Tarihi",null=True,blank=True)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)