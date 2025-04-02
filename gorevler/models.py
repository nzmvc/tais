from django.db import models
from user.models import User, Departments
from ckeditor.fields import RichTextField
from django.utils import timezone
from saas.models import Company
from user.models import Color
from django.utils.crypto import get_random_string
import datetime

# Create your models here.

class GorevType(models.Model):   # kontrol,standart,proje,revizyon
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=30,verbose_name="Hatırlatma Tipi")
    aciklama = models.CharField(max_length=150,verbose_name="Açıklama",blank =True,null=True)
    created_date = models.DateTimeField(default=timezone.now,blank =True,null=True)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)

    def __str__(self):
        return self.type
  
class DuzenliGorevTanim(models.Model):
    TEKRAR_TIPLERI = (
        ('1', 'Günlük'),
        ('2', 'Haftalık'),
        ('3', 'Aylık'),
        ('4', 'Yıllık'),
        ('5', 'Saatlik'),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, verbose_name="Düzenli Görev Başlığı")
    description = RichTextField(verbose_name="Görev Detayları", blank=True, null=True)
    start_date = models.DateField(verbose_name="Başlangıç Tarihi",default=timezone.now)
    end_date = models.DateField(verbose_name="Bitiş Tarihi", blank=True, null=True)
    
    repeat_type = models.CharField(max_length=1, choices=TEKRAR_TIPLERI, default='1', verbose_name="Tekrar Tipi")
    frequency = models.IntegerField(default=1, verbose_name="Tekrar Sıklığı")
    days_of_week = models.JSONField(blank=True, null=True, verbose_name="Haftanın Günleri")
    days_of_month = models.JSONField(blank=True, null=True, verbose_name="Ayın Günleri")
    
    department = models.ForeignKey(Departments, verbose_name="Departman", null=True, blank=True, on_delete=models.SET_NULL)
    color = models.ForeignKey(Color, verbose_name="Renk", on_delete=models.SET_NULL, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    created_user = models.ForeignKey(User, verbose_name="Kaydı Açan",related_name="duzenliGorevCreatedUser",null=True,blank=True,on_delete=models.SET_NULL)
    responsible_user = models.ForeignKey(User,verbose_name="Görev Sorumlusu",related_name="duzenliGorevresUser",on_delete=models.PROTECT,null=True,blank=True)
    document = models.FileField(blank=True, null=True, verbose_name="Döküman (Varsa)")
    
    numberOfDayOpen = models.IntegerField(default=3, verbose_name="Açık Kalma Gün Sayısı")
    numberOfDayCreate = models.IntegerField(default=3, verbose_name="Kaç gün önce oluşturulacak")
    
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    company = models.ForeignKey(Company, on_delete=models.PROTECT, default=1)
    def __str__(self):
        return self.title
      
class GorevlerStatu (models.Model):
    id = models.AutoField(primary_key=True)
    statu = models.CharField(max_length=30,verbose_name="Gorev Statu")
    aciklama = models.CharField(max_length=150,verbose_name="Açıklama",blank =True,null=True)
    created_date = models.DateTimeField(default=timezone.now,blank =True,null=True)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)
    color = models.ForeignKey(Color,verbose_name="Renk",on_delete=models.SET_NULL,blank=True,null=True)
    is_end = models.BooleanField(verbose_name="Görev Sonlandırma",default=False)
    is_start = models.BooleanField(verbose_name="Görev Başlatma",default=False)

    def __str__(self):
        return self.statu

class Gorevler (models.Model): 
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150,verbose_name="Görev Başlığı")
    type = models.ForeignKey(GorevType,verbose_name="Görev Tipi",null=True,blank=True,on_delete=models.SET_NULL)
    scheduledTask = models.ForeignKey(DuzenliGorevTanim,verbose_name="Düzenli Görev",null=True,blank=True,on_delete=models.SET_NULL)    
    description = RichTextField(verbose_name="Görev Detayları",blank =True,null=True)
    solution = RichTextField(verbose_name="Tamamlama Özeti",blank =True,null=True)
    created_date =  models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(verbose_name="Planlanan Başlangıç Tarihi",blank =True,null=True)
    deadline = models.DateTimeField(verbose_name="Planlanan Bitiş Tarihi",blank =True,null=True)
    open_user = models.ForeignKey(User, verbose_name="Kaydı Açan",related_name="openUser",null=True,blank=True,on_delete=models.SET_NULL)
    responsible_user = models.ForeignKey(User,verbose_name="Görev Sorumlusu",related_name="resUser",on_delete=models.PROTECT,null=True,blank=True)
    department = models.ForeignKey(Departments,verbose_name="Departman",null=True,blank=True,on_delete=models.SET_NULL)
    closed_date = models.DateTimeField(blank =True,null=True)
    dokuman = models.FileField(blank =True,null=True,verbose_name="Döküman")
    statu = models.ForeignKey(GorevlerStatu,default=1,null=True,blank=True,on_delete=models.SET_NULL)
    secret = models.CharField(max_length=50, verbose_name="Job secret")
    secret_expiredate = models.DateTimeField(blank =True,null=True,verbose_name="Secret Geçerlilik Tarihi")
    complete_level = models.IntegerField(default=0,verbose_name="Tamamlanma Oranı")
    harcama = models.FloatField(default=0,verbose_name="Harcama")
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)

    revision = models.IntegerField(verbose_name="Revizyon",default=1)
    res_user_name = models.CharField(verbose_name="Sorumlu Ad/Soyad",max_length=30,blank=True, null=True)
    res_user_telephone = models.CharField(verbose_name="Sorumlu kullanıcı telefonu",max_length=20,blank=True, null=True)
    res_user_email = models.CharField(verbose_name="Sorumlu kullanıcı email",max_length=20,blank=True, null=True)
    planed_startdate = models.DateField(blank=True, null=True)
    planed_date = models.DateField(blank=True, null=True)
    revision_date =models.DateTimeField(blank=True, null=True)

    latitude = models.FloatField(null=True, blank=True) 
    longitude = models.FloatField(null=True, blank=True) 
    priority = models.IntegerField(default=3) # 1-5 arasında öncelik puanı

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = get_random_string(length=50).upper()
            self.secret_expiredate = timezone.now() + datetime.timedelta(days=7)
        if not self.created_date:
            self.created_date = timezone.now()

        super(Gorevler, self).save(*args, **kwargs)

class GorevNotu(models.Model):
    id = models.AutoField(primary_key=True)
    gorev = models.ForeignKey(Gorevler,verbose_name="gorev",on_delete=models.CASCADE)
    created_date = models.DateTimeField()
    open_user = models.ForeignKey(User, verbose_name="Kayıdı açan",null=True,blank=True,on_delete=models.SET_NULL)
    description = RichTextField(verbose_name="Açıklama",blank =True,null=True)
    dokuman = models.FileField(blank =True,null=True,verbose_name="Döküman")
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)

class ReminderType(models.Model):   # sms ,mail ,push notification ,app,web,whatsapp
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=30,verbose_name="Hatırlatma Tipi")
    aciklama = models.CharField(max_length=150,verbose_name="Açıklama",blank =True,null=True)
    created_date = models.DateTimeField(default=timezone.now,blank =True,null=True)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)

    def __str__(self):
        return self.type

class  Reminder(models.Model):
    zamanTipi = (
        ('1','Dakika'),
        ('2','Saat'),
        ('3','Gün'),
        ('4','Hafta'),
        ('5','Ay'),
    )
    id = models.AutoField(primary_key=True)
    gorev = models.ForeignKey(Gorevler,verbose_name="gorev",on_delete=models.CASCADE,blank=True,null=True)
    created_date = models.DateTimeField()
    open_user = models.ForeignKey(User, verbose_name="Kayıdı açan",null=True,blank=True,on_delete=models.SET_NULL)
    description = models.CharField(max_length=100,verbose_name="Hatırlatma Açıklaması",blank =True,null=True)
    reminder_date = models.DateTimeField(verbose_name="Hatırlatma Tarihi",null=True,blank=True)
    type = models.ForeignKey(ReminderType,verbose_name="Hatırlatma Tipi",null=True,blank=True,on_delete=models.SET_NULL)
    time = models.IntegerField(verbose_name="Ne kadar önceden hatırlatılsın",default=1)
    time_type = models.CharField(verbose_name="Saat / Gün / Hafta ...",max_length=1,choices=zamanTipi,default='3')
    company= models.ForeignKey(Company,on_delete=models.PROTECT,default=1)
    

