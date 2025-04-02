from django.db import models
from user.models import User,Employee,Sube,Departments
import datetime
from django.utils import timezone
from saas.models import Company


# Create your models here.

class DokumanTipi (models.Model):
    id = models.AutoField(primary_key=True)
    tip = models.CharField(verbose_name="Dokuman Tipi" ,max_length=20)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)
    def __str__(self):
        return self.tip

class Dosyalar (models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(verbose_name="Dosya")
    aciklama = models.CharField(max_length=100,verbose_name="Açıklama",null=True,blank=True)
    type = models.ForeignKey(DokumanTipi,verbose_name="Dokuman Tipi",on_delete=models.PROTECT)
    created_date = models.DateField(verbose_name="Eklenme Tarihi",default=timezone.now)
    created_user = models.ForeignKey(User,verbose_name="Ekleyen kullanıcı",on_delete=models.PROTECT)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)
    secret = models.CharField(max_length=100,verbose_name="Job secret",blank=True, null=True)       
    secret_valid = models.DateField(verbose_name="Secret Geçerlilik Tarihi",blank=True, null=True)
    def __str__(self):
        return self.file.name

