from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from saas.models import Company
import datetime

from django.contrib.auth.models import User



#User.__str__ = lambda user_instance: user_instance.first_name + " " + user_instance.last_name

def profile_upload_to(instance, filename):
    """Dosyanın yüklenme yolu ve adını özelleştirmek için bir fonksiyon."""
    formatted_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # YYYYMMDD formatında tarih
    new_filename = f"{formatted_date}_{filename}"
    return new_filename

class Departments(models.Model):
    id = models.AutoField(primary_key=True)
    department_number = models.CharField(max_length=150, unique=True)
    title = models.CharField(max_length=150, unique=True)
    description = models.TextField(max_length=500,blank=True,null=True)
    company= models.ForeignKey(Company,on_delete=models.PROTECT,blank=True,null=True)
    main_department = models.ForeignKey("self",on_delete=models.PROTECT,blank=True,null=True)

    def __str__(self):
        return self.title

class Color(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, unique=True)
    color = models.CharField(max_length=10,verbose_name="Renk Kodu(bootstrap)",null=True,blank=True)
    color_code = models.CharField(max_length=60,verbose_name="Renk Kodu(rgb)",null=True,blank=True)
    satir_color_code = models.CharField(max_length=60,verbose_name="Satır Renk Kodu(rgb)",null=True,blank=True)

    def __str__(self):
        return self.title
    
class Sube(models.Model):
    id = models.AutoField(primary_key=True)
    
    title = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.title

class Yetenek(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.title

class Yetki(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.title

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE) #,related_name="user" user tablosundaki her kaydın burada bir karşılığı var.
    profilePhoto = models.FileField(blank =True,null=True,verbose_name="Problem dosya/resim",upload_to=profile_upload_to)
    department = models.ForeignKey(Departments,on_delete=models.PROTECT,verbose_name="Departman",blank=True,null=True)
    role = models.CharField(max_length=20,blank=True,default="Kullanıcı")
    telephone = models.CharField(max_length=30,verbose_name="Telefon(iş)",blank=True,null=True)
    telephone2 = models.CharField(max_length=30,verbose_name="Telefon(şahsi)",blank=True,null=True)
    sube = models.ForeignKey(Sube,on_delete=models.PROTECT,verbose_name="Şube",blank=True,null=True)
    yetenek =  models.TextField(max_length=500,blank=True,null=True,verbose_name="Yetenek")
    company= models.ForeignKey(Company,on_delete=models.PROTECT,blank=True,null=True)
    otp = models.CharField(max_length=4,blank=True,null=True)
    otp_expiredate = models.DateTimeField(blank=True,null=True)
    otp_attemp = models.IntegerField(default=0,verbose_name="Telefon doğrulama deneme sayısı")
    about = models.TextField(max_length=500,blank=True,null=True,verbose_name="Hakkımda")
    education = models.TextField(max_length=500,blank=True,null=True,verbose_name="Eğitim")
    experience = models.TextField(max_length=500,blank=True,null=True,verbose_name="Deneyim")
    tcno = models.CharField(max_length=11,blank=True,null=True,verbose_name="TC Kimlik No")
    passport = models.CharField(max_length=20,blank=True,null=True,verbose_name="Pasaport No")
    isAdmin = models.BooleanField(default=False,verbose_name="Firma Admin")
    def __str__(self):
        #return self.user.username
        
        return self.user.first_name + " " + self.user.last_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    
    if created:
        Employee.objects.create(user=instance)
        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.employee.save()

class SmsProblem(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField( auto_now=True)
    telephone = models.CharField(max_length=20,verbose_name="Telefon")
    message = models.TextField(max_length=500,verbose_name="Mesaj")
    status = models.CharField(max_length=3, verbose_name="Status",default="10",blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    send_date = models.DateTimeField(blank=True,null=True)
    last_error = models.CharField(max_length=15, verbose_name="Status",default="10",blank=True,null=True)
    try_count = models.IntegerField(default=0,verbose_name="Deneme sayısı")

class Logging(models.Model):
    #log type = workflow,order,user,customer,general
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField( auto_now=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    log_type = models.CharField(max_length=20,verbose_name="Açıklama",default="genel")
    type_id = models.IntegerField(verbose_name="Order ID",default=1)
    aciklama = models.CharField(max_length=100,verbose_name="Açıklama")
    status = models.CharField(max_length=3, verbose_name="Status",default="10",blank=True,null=True)

class ShortCut(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100,verbose_name="Başlık")
    url = models.CharField(max_length=200,verbose_name="Url")
    icon = models.CharField(max_length=50,verbose_name="Icon",default="fas fa-home")
    color = models.ForeignKey(Color,on_delete=models.PROTECT,verbose_name="Renk",default=1)
    order = models.IntegerField(verbose_name="Sıra",default=1)

class Yetkilendirme(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        permissions = (
                        ("siparis_yonetimi", "Satış girişi için gerekli yetki"),
                        ("siparis_listele","Satışları listeleme"),
                        ("urun_listele","Ürün Listeleme"),
                        ("urun_yonetim","Ürün ekleme,güncelleme,deaktif etme"),
                        ("musteri_listele","Müşteri listeleme"),
                        ("musteri_yonetim","Müşteri ekleme,güncelleme,silme"),
                        ("kullanici_listeleme", "Kullanıcı listeleme"),
                        ("kullanici_yonetim", "Kullanıcı yönetimi"),
                        ("rezervasyon_listele","Rezervasyonları listeleme görüntüleme"),
                        ("rezervasyon_yonetim","Rezervasyon yönetim işlemleri"),
                        ("rapor_listele","Rapor listeleme"),
                        ("log_listeleme","Logları görme"),
                        ("musterisikayet_listeleme","Müşteri şikayetleri listele gör"),
                        ("musterisikayet_yonetim","Müşteri şikayetleri yönetimi"),
                        ("workflow_operasyon","Workflow Operasyon "),
                        ("workflow_planlama","Workflow Planlama  "),
                        ("workflow_depo","Workflow Depo "),
                        ("workflow_uretim","Workflow Uretim "),
                        ("workflow_islem","Workflow üzerinde işlem yapabilme yetkisi "),
                        ("test","test yetkisi"),
                       
                      )

    