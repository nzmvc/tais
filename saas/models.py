import os
from unicodedata import name
from django.db import models
import datetime
from django.utils import timezone
from user.models import User,Group

# Create your models here.

class Sector(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,verbose_name="Sektor Adı")
        
    def __str__(self):
        return self.name

class CompanyStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,verbose_name="Durum Adı")
    description = models.CharField(max_length=200,verbose_name="Açıklama",null=True,blank=True)
    active = models.BooleanField(verbose_name="Aktif/Pasif",default=True)
    created_date = models.DateTimeField(verbose_name="Oluşturulma tarihi",default=timezone.now)
    
    def __str__(self):
        return self.name
    
class Company (models.Model):
    id = models.AutoField(primary_key=True)
    status = models.ForeignKey(CompanyStatus,verbose_name="Durum",on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=100,verbose_name="Firma Adı")
    adres = models.CharField(max_length=200,verbose_name="Adres",null=True,blank=True)
    telefon = models.CharField(max_length=30,verbose_name="Telefon",null=True,blank=True)
    email = models.CharField(max_length=100,verbose_name="Email",null=True,blank=True)
    web = models.CharField(max_length=100,verbose_name="Web Sayfası",null=True,blank=True)
    logo = models.ImageField(upload_to="logo/",verbose_name="Logo",null=True,blank=True)
    description = models.CharField(max_length=200,verbose_name="Açıklama",null=True,blank=True)
    active = models.BooleanField(verbose_name="Aktif/Pasif",default=True)
    created_date = models.DateTimeField(verbose_name="Oluşturulma tarihi",default=timezone.now)
    user = models.ForeignKey(User,verbose_name="Sorumlu",on_delete=models.CASCADE,null=True,blank=True)
    sector = models.ForeignKey(Sector, verbose_name="Sektor",on_delete=models.PROTECT,null=True,blank=True)
    faturaDetay = models.TextField(verbose_name="Fatura DetayBilgileri",null=True,blank=True)
    vergi_dairesi = models.CharField(max_length=100,verbose_name="Vergi Dairesi",null=True,blank=True) 
    vergi_no = models.CharField(max_length=100,verbose_name="Vergi Numarası",null=True,blank=True)

    def __str__(self):
        return self.name

class Modules(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,verbose_name="Modül Adı")
    description = models.CharField(max_length=200,verbose_name="Açıklama",null=True,blank=True)
    userGroup = models.ForeignKey(Group,verbose_name="Kullanıcı Grubu",on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(verbose_name="Aktif/Pasif",default=True)
    created_date = models.DateTimeField(verbose_name="Oluşturulma tarihi",default=timezone.now)
    
    
    def __str__(self):
        return self.name

class CompanyModules(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company,verbose_name="Firma",on_delete=models.CASCADE)
    modules = models.ForeignKey(Modules,verbose_name="Modül",on_delete=models.CASCADE)
    active = models.BooleanField(verbose_name="Aktif/Pasif",default=True)
    created_date = models.DateTimeField(verbose_name="Oluşturulma tarihi",default=timezone.now)
    expire_date = models.DateTimeField(verbose_name="Bitiş Tarihi",null=True,blank=True)
    
    def __str__(self):
        return self.company.name + " - " + self.modules.name
    
class Company_Address(models.Model):
    id = models.AutoField(primary_key=True)
    ulke = models.CharField( max_length=30,verbose_name="ULKE",default="Türkiye")
    il = models.CharField( max_length=30,verbose_name="IL",null=True,blank=True)
    ilce = models.CharField( max_length=30,verbose_name="İLÇE",null=True,blank=True)
    mahalle = models.CharField( max_length=30,verbose_name="MAHALLE",null=True,blank=True)
    adres = models.CharField( max_length=100,verbose_name="ADRES",null=True,blank=True)
    map_link = models.CharField( max_length=100,verbose_name="GOOGLE MAP",null=True,blank=True)
    aciklama = models.CharField( max_length=10,verbose_name="Açıklama(kısa/kod)",null=True,blank=True)
    active = models.BooleanField(default=True)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)



