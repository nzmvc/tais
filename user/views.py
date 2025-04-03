import datetime
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
import notification
from gorevler.models import Gorevler
from .forms import RegisterForm,LoginForm,UserUpdateForm,ChangePassword,EmployeeUpdateForm,DepartmentForm
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User,Permission,Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required   
from .models import  Logging
# Create your views here.
from user.models import Employee,Logging,Departments
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.db.models import Q,Sum,Count

from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.express as px
import pandas as pd
import numpy as np
from decouple import config
from saas.models import Company, CompanyModules, CompanySettings,Modules,Modules, Settings
import requests,random
from django.http import HttpResponseForbidden, JsonResponse
import time
from django.conf import settings
import saas


# views.py

#######################################################

def Logla(request,message):

    filename = "log.txt"
    #ip = request.META['REMOTE_ADDR']        # client in ip bilgisi alınır
    ip = request.META.get('HTTP_X_REAL_IP')

    try:
        company = request.session['company']    # client eğer login olmuş ise company bilgisi session içerisinde mevcuttur.
        companyName = request.session['companyName']
    except:
        # eğer login değilse 
        # ( örnek olarak ustalar ve müşteriler login olmadan bizim gönderdiğimiz sms linkleri ile sayfa görüntülemekte)
        #bu durumda deafult 1 kaydeder
        company = 0                             
        companyName = "NONE"
        

    # request.user >> login olanlar için sistemde tanımlı kullnıcı adıdır.
    # login olmadan girenler için AnonymousUser şeklinde geçer
        
    with open(filename,"a", encoding="utf-8") as d:
        d.write( f'{datetime.datetime.now()}-IP:{ip}-user:{request.user}-company_id:{company}-company_name:{companyName}-message:{message} \r' )



def LoglaSms(request,message):
    filename = "logSms.txt"
    ip = request.META.get('HTTP_X_REAL_IP')        # client in ip bilgisi alınır

    try:
        company = request.session['company']    # client eğer login olmuş ise company bilgisi session içerisinde mevcuttur.
    except:
        # eğer login değilse 
        # ( örnek olarak ustalar ve müşteriler login olmadan bizim gönderdiğimiz sms linkleri ile sayfa görüntülemekte)
        #bu durumda deafult 1 kaydeder
        company = 0                             
        

    # request.user >> login olanlar için sistemde tanımlı kullnıcı adıdır.
    # login olmadan girenler için AnonymousUser şeklinde geçer
        
    with open(filename,"a", encoding="utf-8") as d:
        d.write( f'{datetime.datetime.now()}-IP:{ip}-user:{request.user}-company_id:{company}-message:{message} \r' )


def companySettingsAdd(company_id):  
    # registeration da firma eklendikten sonra default özelliklerin hepsi 1 tanımlanır.
    # tüm özellik bilgileri Setting tablosunda bulunur.
    # örnek "rezervasyon sonrasında müşteriye sms gonderilecek mi" yada mail atılacak mı? gibi...
    # bu fonksiyon sadece register aşamasında çalışır. 
    set_list = Settings.objects.all()   # tüm özellikler alınır

    for sett in set_list:
        cs= CompanySettings(deger="1",company_id=company_id,settings=sett)  
        cs.save()

    if CompanySettings.objects.filter(company_id=company_id).count() > 0:   # özellilk eklenmiş ise True döndürülür
        return True
    else:
        return False
    
def userControl(phone,email):
    # öncelikle telefon numarası ile kontrol yapılır. eğer telefon numarası var ise hata döndürülür.
    # username olarak telefon tanımlanmamış ise True döndürülür.
    # eğer telefon numarası yok ise email kontrolü yapılır. username olarak email tanımlanmamış ise True döndürülür.
    if phone :
        print("phone",phone)  
        userName = phone.replace("+","").replace(" ","").replace("(","").replace(")","").replace("-","")
        if userName[0] != "0":
            userName = "0"+userName
           
        user= User.objects.filter(username=userName)  
        if user.count() > 0:
            return user[0]
        else:
            return False
    elif email:
        print("email",email)
        user= User.objects.filter(username=email)
        if user.count() > 0:
            return user[0]
        else:
            return False
    else:  
        return False
    
def modulEkle(request,company):
    #TODO: istenen moduller eklenmeli. su an tabloda tanımlanmış hepsini ekliyoruz
    try:
        for m in Modules.objects.all():
            cm = CompanyModules(company=company,modules=m)
            cm.save()
        Logla(request,f'Moduller eklendi {company.name}')
        return True
    except Exception as e:
        print("modul eklemede hata : "+ str(e))
        Logla(request,f'Moduller eklemede hata : {str(e)} ')
        return False

def gruplaraEkle(request,newUser):
    # Register olan admin kullnaıcısı için aşagıdaki gruplar tanımlanır.
    group_names = [
        "company_admin",
    ]
    # Grupları kullanıcıya ekle
    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
            newUser.groups.add(group)
            Logla(request,f"{group_name} grup eklemelesi yapıldı")
        except Group.DoesNotExist:
            print(f"Group '{group_name}' does not exist.")
            Logla(request,f"Group '{group_name} eklerken hata oluştu")
            
    
           
def createUserAndCompany(request,email,phone):
    try:
        #userName = phone if phone != "" else email
        randomPassword = str(random.randint(100000,999999))
        userName = phone.replace("+","").replace(" ","").replace("(","").replace(")","").replace("-","")
        #newUser = User( username = userName, email=email,is_active=0)
        newUser = User( username = userName,is_active=0)
        newUser.set_password(randomPassword)
        newUser.save()
        print("user eklendi")
        Logla(request,f"user:{newUser} eklendi.")
        
        newUser.employee.telephone = phone     # user ile employee tablosu onetoone bağlı
        newUser.employee.otp = str(random.randint(1000,9999))   #otp one time password
        newUser.employee.otp_expiredate = datetime.datetime.now() + datetime.timedelta(minutes=2) # 2 dk içinde telefon doğrulaması yapılmalı
        newUser.employee.isAdmin = 1
        newUser.employee.save()
        print("employee eklendi")
        Logla(request,f" employee eklendi.")
        
        # kullanıcı tüm gruplara dahil edilir
        gruplaraEkle(request,newUser) 
        print("gruplar eklendi")
        
        company = Company(name=userName, telefon=phone, email=email, user = newUser )
        company.save()
        Logla(request,f'Firma Eklendi {company.name}')
        print("firma eklendi")
        
        # firmaya tüm modüller eklenir
        modulEkle(request,company)
        print("moduller eklendi")
        Logla(request,"modul eklendi")
        
        newUser.employee.company_id = company.id   # kullanıcının employee tablosuna company bilgisi güncellendi
        newUser.employee.save()
        Logla(request,f'Firmaya user Eklendi user:{newUser} {company.name}')
        
        if not companySettingsAdd(company.id) :
            messages.warning(request,"Firma ayarlarında hata, 05326179630 u arayın!")
            notification.views.send_sms(request,"0905326179630",f"yetkilendirme hatası {company}")
            print("firma setting ayarlandı")
            Logla(request,f'Firma Yetkinlendirmede hata !!! ')
                        
        return newUser,company,newUser.employee.otp
    
    except Exception as e:
        print("user yada firma tanımlamada hata : "+ str(e))
        messages.error(request,"user yada firma tanımlamada hata : "+ str(e))
        Logla(request,"user yada firma tanımlamada hata : "+ str(e))
        return False

def reSendActivation(request,phone,email):
    #TODO: güvenlik için birşey düşünelim. şu an herkesin telefonuna kod gönderilebilir.
    
    try:
        if phone != "":
            user = User.objects.get(username=phone)
        else:
            user = User.objects.get(username=email)
            
        print("user",user)
        user.employee.otp = str(random.randint(1000,9999))
        user.employee.otp_expiredate = datetime.datetime.now() + datetime.timedelta(minutes=2) # 2 dk içinde telefon doğrulaması yapılmalı
        user.employee.save()
        company = Company.objects.get(user=user)
        
        sendActivation(request,user,company,user.employee.otp,phone,email)
        print("link TEKRAR gönderilecek")
    
        messages.info(request,"Doğrulama kodu tekrar gönderildi")
        Logla(request,f'Doğrulama kodu tekrar gönderildi {user}')
        return render(request,"telephoneConfirm.html")
    except Exception as e:
        messages.error(request,"Kullanıcı bulunamadı")
        Logla(request,f'Kullanıcı bulunamadı {phone} {email} hata:{str(e)} ')
        return redirect("/user/register")
    
def userConfirm(request,userName,otp):
    # burası sadece botları ayırmak için kullanılır.
    # botlar bu sayfaya gelirse bot olduğu anlaşılır ve işlem yapılmasına izin verilmez.
    try:
        user = User.objects.get(username=userName)
        if user.is_active == 0  and user.employee.otp == otp and datetime.datetime.now() < user.employee.otp_expiredate:
            scheme = request.is_secure() and "https" or "http"
            hostname =  f'{scheme}://{request.get_host()}/'
            simpleLoginLink = f"{hostname}user/simpleLogin/{userName}/{otp}"
            
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            print("user_agent",user_agent)
            return render(request,"userRegisterConfirm.html",{ 'simpleLoginLink':simpleLoginLink})
        
        else:
            messages.warning(request,"Kullanıcı aktif edilemedi. Linkin süresi dolmuş olabilir. Aynnı Numara ile tekrar kayıt deneyiniz. Yeni aktivasyon linki gönderilecektir.")
            Logla(request,f'Kullanıcı aktif edilemedi {userName} . Linkin süresi dolmuş olabilir.')
            return redirect("/user/simpleRegister")
    except Exception as e:
        messages.error(request,"Kullanıcı bulunamadı")
        Logla(request,f'Kullanıcı bulunamadı {userName}  hata:{str(e)} ')
        return redirect("/user/simpleRegister")

    

def simpleLogin(request,userName,otp):
    print("simpleLogin çalışıyor")
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    print("user_agent",user_agent)
    if "whatsapp" in user_agent or "bot" in user_agent:
        print("bot tespiti yapıldı")
        return HttpResponseForbidden("Bot tespiti yapıldı.")
    
    try:
        user = User.objects.get(username=userName)
        if user.is_active == 0  and user.employee.otp == otp and datetime.datetime.now() < user.employee.otp_expiredate:
            user.is_active = 1
            randomPassword = str(random.randint(100000,999999))
            user.set_password(randomPassword)
            user.save()
            print("user aktif edildi")
            messages.info(request,"Kullanıcı aktif edildi sistemi kullanmaya başlayabilirsiniz.")
            Logla(request,f'Kullanıcı aktif edildi {userName}')
            login(request,user)
            
            company = user.employee.company
            company_id = company.id                     # kullanıcının firma bilgisi alınır

            request.session['company'] = company_id         # session içerisini company_id bilgisi company adında saklanır. sonraki sayfalarda bu kullanılır
            request.session['companyName'] = company.name   # companyname de session içerisinde tutulur.
    

            
            if company.logo :                               # firmanın logosu sisteme yüklenmiş ise bu da session a atılır
                request.session['companyLogoUrl'] = company.logo.url
                #print(company.logo.url)
                
            print("session a company bilgileri atıldı")

            scheme = request.is_secure() and "https" or "http"
            hostname =  f'{scheme}://{request.get_host()}/'
            webLink = f"{hostname}/user/login"
            wellcome_msg = f"Sistemimize hoşgeldiniz. Kullanıcı adınız : {userName} Şifreniz : {randomPassword} link: {webLink}"
            
            if saas.views.getSettings("registration_sms",1):
                #messages.warning(request,"sms gönderimi yapılacak")
                print("register sms gönderilecek")
                if user.employee.telephone:
                    print("telefon var")
                    try:
                        notification.views.send_sms(request,user.employee.telephone,wellcome_msg)
                        notification.views.whatsappMessage(request,user.employee.telephone,wellcome_msg)
                        #messages.info(request,"Erişim bilgileri telefonunuza gönderildi")
                        print("register sms gonderildi")
                    except Exception as e:
                        print("sms veya whatsapp gonderiminde hata : "+ str(e))
                        messages.error(request,"sms veya whatsapp gonderiminde hata : "+ str(e))
                        Logla(request,f'Sms veya whatsapp Gönderiminde hata phone:{user.employee.telephone}  hata:{str(e)} ')
                else:
                    print("telefon yok")
                    messages.warning(request,"Telefon numarası yok")
                    Logla(request,f'Telefon numarası yok {userName} ')
            else:
                print("registration sms gönderilmeyecek.settings de kapalı")    
            return redirect("/user/moduleDocs/")
        else:
            messages.warning(request,"Kullanıcı aktif edilemedi. Linkin süresi dolmuş olabilir. Aynnı Numara ile tekrar kayıt deneyiniz. Yeni aktivasyon linki gönderilecektir.")
            Logla(request,f'Kullanıcı aktif edilemedi {userName} . Linkin süresi dolmuş olabilir.')
            return redirect("/user/simpleRegister")
    except Exception as e:
        messages.error(request,"Kullanıcı bulunamadı")
        Logla(request,f'Kullanıcı bulunamadı {userName}  hata:{str(e)} ')
        return redirect("/user/simpleRegister")
    
def sendActivation(request,newUser,company,otp,phone,email):
    
    scheme = request.is_secure() and "https" or "http"
    hostname =  f'{scheme}://{request.get_host()}/'
    #simpleLoginLink = f"{hostname}user/simpleLogin/{newUser}/{otp}"
    simpleLoginLink = f"{hostname}user/userConfirm/{newUser}/{otp}"
    """
    msg_html = render_to_string("email_wellcome.html",{'company':company,'newUser':newUser,'link':simpleLoginLink})
    
    if saas.views.getSettings("registration_mail",1):      #ayarlarda mail gönderin aktif ise gönderim yapılır
        print("mail gönderilecek")
        try:
            send_mail(subject="TOYU - HOŞ GELDİNİZ",
                    #message=f"Aktivasyon için linki tıklayınız . {simpleLoginLink} sorularınız için 0532 617 96 30",
                    message="",
                    html_message=msg_html,
                    from_email="info@toyu.app",
                    recipient_list=[email,"nzm.avci@gmail.com"], 
                    fail_silently=False)
            print("mail gonderildi")
            Logla(request,f'Mail Gönderildi {email} ')
        except Exception as e:
            print("mail gonderiminde hata : "+ str(e))
            messages.error(request,"Mail gonderiminde hata : "+ str(e))
            Logla(request,f'Mail Gönderiminde hata {email} ')
    """
    
    if saas.views.getSettings("registration_sms",1):
        #messages.warning(request,"sms gönderimi yapılacak")
        print("sms gönderilecek")
        try:
            notification.views.send_sms(request,phone,f"Aktivasyon için tıklayın {simpleLoginLink} Destek için: 05326179630")
            notification.views.send_sms(request,"5326179630",f"Yeni firma !!! Firmaniz eklendi:{company} user:{email} ")
            notification.views.whatsappMessage(request,phone,f"Aktivasyon için tıklayın {simpleLoginLink} Destek için: 05326179630")
            #messages.info(request,"Aktivasyon linki telefonunuza gönderildi linki tıklayınız")
            print("sms gonderildi")
        except Exception as e:
            print("sms veya whatsapp gonderiminde hata : "+ str(e))
            messages.error(request,"sms veya whatsapp gonderiminde hata : "+ str(e))
            Logla(request,f'Sms veya whatsapp Gönderiminde hata phone:{phone}  hata:{str(e)} ')
                    
                    
def simpleRegister(request): # kullanıcı kayıt sayfası
    # sadece telefon numarası ve email adresi ile kayıt olunur.
    # kayıt olunan kullanıcıya aktivasyon linki gönderilir.
    # aktivasyon linki 2 dk geçerlidir.
    # aktivasyon linki tıklandığında kullanıcı aktif edilir ve sisteme giriş yapabilir.
    
    if request.method == 'POST':    # post methodu ile gelen veriler alınır
       
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        checkboxKullanim = request.POST.get("checkboxKullanim")
        checkboxKVKK = request.POST.get("checkboxKVKK")
        
        phone = phone.replace("+","").replace(" ","").replace("(","").replace(")","").replace("-","")
    
        if checkboxKullanim == None or checkboxKVKK == None:
            messages.warning(request,"Kullanım  ve KVKK koşullarını kabul etmelisiniz")
            return render(request,'simpleRegister.html')
        if email == "" and phone=="" :
            messages.warning(request,"Email yada Telefon bilgisi girilmelidir")
            return render(request,'simpleRegister.html')
        
        #########################################################################
        # reCAPTCHA doğrulamasını kontrol et
        # bunu için goole de ayarların yapılmış olması gerekiyor.
        # Gerekli key bilgileri setting dosyasına işlendi
        recaptcha_response = request.POST.get('g-recaptcha-response')
        ##### json data oluşturularak google dan bilgi alınız
        data = {
            'response': recaptcha_response,
            'secret': settings.RECAPTCHA_PRIVATE_KEY
        }
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result_json = resp.json()
        #########################################################################
        
        if result_json.get('success'):          # robot kontrolu yaptık
            
            user = userControl(phone,email)
            if user == False:    # kullanıcı daha önce tanımlı değilse
                print("user tanımlanacak")
                try:
                    # kullanıcı ve firma tanımlanır.otp oluşturulur
                    newUser,company,otp = createUserAndCompany(request,email,phone)
                    print("newUser",newUser)
                    
                    if newUser :
                        
                        print("link gönderilecek")
                        # aktivasyon linki gönderilir.
                        sendActivation(request,newUser,company,otp,phone,email)
                        
                        # activasyon bekleme sayfasına yönlendirilir.
                        # aktivaston linki nereden tıklanırsa tıklansın bu sayfa
                        # aktivasyon u algılar ve ilk giri sayfasına yönlendirir
                        return render(request,"activation_status_check.html",{'phone':phone,'email':email})
                        # return redirect(f"/user/telephoneConfirm/{newUser.id}")
                
                except Exception as e:
                    messages.error(request,"user yada firma tanımlamada hata : "+ str(e))
                    Logla(request,f'Firma tanımlamada hata: {str(e)} ')
                    print("user yada firma tanımlamada hata : "+ str(e))
                    
            elif user.is_active == False: # kullanıcı daha önce tanımlandmış ise
                print("kullanıcı tanımlı fakat aktif olmamış")
                print("user id:",user.id)
                messages.warning(request,"Kullanıcı zaten tanımlı telefon yada email adresi kullanılmış.")
                
                # tekrar aktivasyon linki gönderilir
                # TODO: süreçsel olarak tekrar düşünelim
                
                reSendActivation(request,phone,email)
                
                print("Kullanıcı zaten tanımlı. Aktivasyon linki gönderildi")
                # kullanıcı daha önce tanımlı ise tekrar aktivasyon linki gönderilir
                # !!!!!!!!!!!burada otomatik login olunmamalı. daha önce kullanıcı sisteme giriş yapmış olabilir.
                return redirect("/user/login")
            else:
                messages.warning(request,"Kullanıcı zaten aktif. Şifre sıfırlama yapabilirsiniz.")
                print("Kullanıcı zaten aktif")
                return redirect("/user/login")
        else:
            Logla(request,f'reCAPTCHA doğrulaması başarısız {email} {phone} ')
            print("reCAPTCHA doğrulaması başarısız lütfen tekrar deneyiniz. Problem devam ederse 05326179630 u arayınız")
            messages.warning(request,"reCAPTCHA doğrulaması başarısız lütfen tekrar deneyiniz. Problem devam ederse 05326179630 u arayınız")
            redirect("/user/simpleRegister")
            #return HttpResponse(f"reCAPTCHA doğrulaması başarısız. {result_json}")

    return render(request,'simpleRegister.html',{'site_key': settings.RECAPTCHA_PUBLIC_KEY})

from user.forms import AccountRegisterForm

@login_required(login_url='/user/login/')
@permission_required('auth.add_user',login_url='/user/yetkiYok/')
def accountRegister(request): # kullanıcı kayıt sayfası
    
    form = AccountRegisterForm(request.POST or None)
    
    if request.method == 'POST':    # post methodu ile gelen veriler alınır
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data.get("company")
            name = form.cleaned_data.get("first_name")
            surname = form.cleaned_data.get("second_name")
            email = form.cleaned_data.get("email")
            phone = form.cleaned_data.get("telephone")

            username = createUsername(email,phone,name,surname)     # kullanıcı adı oluşturulur

            newUser = User( username = username,email=email,first_name=name,last_name=surname,is_active=1)
            randomPassword = str(random.randint(100000,999999))
            newUser.set_password(randomPassword)      # sistem üzerinde kullanıcının şifresi tanımlanır.
            newUser.save()
            
            newUser.employee.telephone = phone      # user ile employee tablosu onetoone bağlı
            newUser.employee.isAdmin = 1
            newUser.employee.save()
            Logla(request,f'User Eklendi {newUser}')
        
            # kullanıcı tüm gruplara dahil edilir
            gruplaraEkle(request,newUser) 
            Logla(request,f'Gruplar Eklendi {newUser}')
            print("gruplar eklendi")

            company = Company(name=company_name, telefon=phone, email=email, user = newUser )
            company.save()
            print("firma eklendi")
            Logla(request,f'Firma Eklendi {company.name}')

            # firmaya tüm modüller eklenir
            modulEkle(request,company)
        
            #TODO: istenen moduller eklenmeli. su an tabloda tanımlanmış hepsini ekliyoruz
            
            newUser.employee.company_id = company.id   # kullanıcının employee tablosuna company bilgisi güncellendi
            newUser.employee.save()

            messages.info(request," Firma tanımlandı username : "+username+" şifre : "+randomPassword)
            Logla(request,f'Firmaya user Eklendi user:{newUser} {company.name}')
            notification.views.whatsappMessage(request,"05326179630",f"TOYU uygulamasına hoşgeldiniz. Kullanıcı adınız : {username} Şifreniz : {randomPassword}")
            return redirect("/saas/companyList/active")
    else:
        
        return render(request,"accountRegister.html",{'form':form})


def register(request): # kullanıcı kayıt sayfası

    if request.method == 'POST':    # post methodu ile gelen veriler alınır
        company = request.POST.get("company") # formdan gelen veriler alınır
        name = request.POST.get("name")
        surname = request.POST.get("surname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password") 
        password2 = request.POST.get("password2")
        checkbox = request.POST.get("checkbox")

        if checkbox == None:
            messages.warning(request,"Kullanım koşullarını kabul etmelisiniz")
            return render(request,'register.html')
        if company == "" or name=="" or surname=="" or phone=="" or password=="":
            messages.warning(request,"Bilgiler boş bırakılamaz")
            return render(request,'register.html')
        
        #########################################################################
        # reCAPTCHA doğrulamasını kontrol et
        # bunu için goole de ayarların yapılmış olması gerekiyor.
        # Gerekli key bilgileri setting dosyasına işlendi
        recaptcha_response = request.POST.get('g-recaptcha-response')
        ##### json data oluşturularak google dan bilgi alınız
        data = {
            'response': recaptcha_response,
            'secret': settings.RECAPTCHA_PRIVATE_KEY
        }
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result_json = resp.json()
        #########################################################################
        
        if result_json.get('success'):          # robot kontrolu yaptık
            if password != "" and password == password2:
                
                try:
                    
                    username = createUsername(email,phone,name,surname)     # kullanıcı adı oluşturulur

                    newUser = User( username = username,email=email,first_name=name,last_name=surname,is_active=0)
                    newUser.set_password(password)      # sistem üzerinde kullanıcının şifresi tanımlanır.
                    newUser.save()
                    newUser.employee.telephone = phone      # user ile employee tablosu onetoone bağlı
                    newUser.employee.otp = str(random.randint(1000,9999))   #otp one time password
                    newUser.employee.otp_expiredate = datetime.datetime.now() + datetime.timedelta(minutes=10) # 10 dk içinde telefon doğrulaması yapılmalı
                    newUser.employee.save()
                    Logla(request,f'User Eklendi {newUser}')

                    """# modulleirn hepsini ekliyoruz. daha sonra bunları tekli ekleme çıkartma yapabileceğiz.
                    grp_list = Group.objects.all()
                    for grp in grp_list:
                        grp.user_set.add(newUser)
                        Logla(request,f'{newUser} için grup tanımlaması yapıldı : {grp.name} ')

                    """

                    company = Company(name=company, telefon=phone, email=email, user = newUser )
                    company.save()

                    #TODO: istenen moduller eklenmeli. su an tabloda tanımlanmış hepsini ekliyoruz
                    for m in Modules.objects.all():
                        cm = CompanyModules(company=company,modules=m)
                        cm.save()

                    newUser.employee.company_id = company.id   # kullanıcının employee tablosuna company bilgisi güncellendi
                    newUser.employee.save()


                    """#TODO: istenen moduller eklenmeli. su an tabloda tanımlanmış hepsini ekliyoruz
                    for m in Modules.objects.all():
                        cm = CompanyModules(company=company,modules=m)
                        cm.save()"""

                    Logla(request,f'Firma Eklendi {company.name}')
                    #messages.info(request," Firma tanımlandı")

                    if not companySettingsAdd(company.id) :
                        messages.warning(request,"Firma ayarlarında hata, 05326179630 u arayın!")
                        notification.views.send_sms(request,"0905326179630",f"yetkilendirme hatası {company}")
                        print("firma setting ayarlandı")
                        Logla(request,f'Firma Yetkinlendirmede hata !!! ')

                    # godnerilecek mesajıniçeriği html olarak oluşturulur
                    msg_html = render_to_string("email_wellcome.html",{'company':company,'newUser':newUser.username ,'password':password})
                    
                    if saas.views.getSettings("registration_mail",1):      #ayarlarda mail gönderin aktif ise gönderim yapılır

                        send_mail(subject="TOYU - HOŞ GELDİNİZ",
                                message="Uygulamamızın ücretsiz eğitimlerine katılmak için bizi arayınız . 0532 617 96 30",
                                html_message=msg_html,
                                from_email="info@toyu.app",
                                recipient_list=[email,"nzm.avci@gmail.com"], 
                                fail_silently=False)
                        print("mail gonderildi")
                        Logla(request,f'Mail Gönderildi {email} ')
                    
                    
                    if saas.views.getSettings("registration_sms",1):
                        #messages.warning(request,"sms gönderimi yapılacak")
                        try:
                            notification.views.send_sms(request,phone,f"Firmaniz eklendi:{company} user:{email}  destek:05326179630")
                            notification.views.send_sms(request,"5326179630",f"Yeni firma !!!Firmaniz eklendi:{company} user:{email} ")
                            
                        except:
                            messages.error(request,"sms gonderiminde hata")
                            Logla(request,f'Sms Gönderiminde hata {phone} ')
                   
                    notification.views.send_sms(request,phone,f"TOYU kayıt doğrulama kodu : {newUser.employee.otp} ")

                    return redirect(f"/user/telephoneConfirm/{newUser.id}")
                
                except Exception as e:
                    messages.error(request,"user yada firma tanımlamada hata : "+ str(e))
                    Logla(request,f'Firma tanımlamada hata: {str(e)} ')

            else:
                messages.warning(request,"Şifreler farklı girildi!!!")
        else:
            return HttpResponse(f"reCAPTCHA doğrulaması başarısız. {result_json}")

    return render(request,'register.html',{'site_key': settings.RECAPTCHA_PUBLIC_KEY})

def modulYetkilendir(request,user,company):

    #firmanın sahip olduğu moduller alınır
    modulList = CompanyModules.objects.filter(company=company)

    for ml in modulList:
        grp = ml.module.userGroup
        grp.user_set.add(user)
        Logla(request,f"user:{user} verilen yetki: {grp}")

def telephoneConfirm(request,userid):
    user = User.objects.get(id = userid)
    print("telefon doğrulama",userid)

    if user is None:
        messages.error(request,"Kullanıcı bulunamadı")
        Logla(request,f'Kullanıcı bulunamadı {userid} ')
        return redirect("/user/register")
    
    if request.method == 'POST':
        button_type = request.POST["button_type"]
        print("button_type",button_type)
        if button_type == "resendButton":
            print("resendButton")
            user.employee.otp = str(random.randint(1000,9999))

            user.employee.otp_expiredate = datetime.datetime.now() + datetime.timedelta(minutes=10) # 10 dk içinde telefon doğrulaması yapılmalı
            user.employee.save()
            notification.views.send_sms(request,user.employee.telephone,f"TOYU doğrulama kodu: {user.employee.otp} ")
            messages.info(request,"Doğrulama kodu tekrar gönderildi")
            Logla(request,f'Doğrulama kodu tekrar gönderildi {user}')
            return render(request,"telephoneConfirm.html")
        
        code= request.POST.get("code")  # formdan gelen doğrulama kodu alınır
        print("code",code)

        if user and user.employee.otp == code and user.employee.otp_expiredate > datetime.datetime.now():       # kullanıcı doğrulandı
            print("telefon doğrulandı")

            user.is_active = 1  # kullanıcı aktif edildi
            user.save()
            messages.success(request,"Telefonunuz doğrulandı")
            Logla(request,f'Kullanıcı telefonu doğrulandı user:{user} telefon:{user.employee.telephone} ')

            company_check = Company.objects.filter(user=user)   
            # kullanıcıya firma tanımlanmış mı kontrol edilir. register sureci yarım kalan kullanıcılar sisteme tekrar giriş yapabilir
            # ikinci defa firma tanımlamasını engellemek için bu kontrolü yapıyoruz

            if company_check.count() == 0: # kullanıcıya firma tanımlanmamış ise
                print("kullanıcıya firma tanımlanacak")
                company_name = f"{user.first_name} {user.last_name}"
                company = Company(name=company_name, user = user) # kullanıcının adı ile firma tanımlandı
                company.save()

                user.employee.company_id = company.id   # kullanıcının employee tablosuna company bilgisi eklendi
                user.employee.save()
                Logla(request,f'Firma Eklendi : {company}')

                """cm = CompanyModules(company=company,modules_id=1) # 1: görev yönetimi modulu firmaya eklendi
                cm.expire_date = datetime.datetime.now() + datetime.timedelta(days=14) # demo için 14 gümn  süre ile geçerli
                cm.save()
                Logla(request,f'firma:{company} Modul Eklendi : {cm}')"""
            
            else:
                company = company_check[0]
                print("kullanıcıya firma daha önce tanımlanmış")
                Logla(request,f'kullanıcı:{user}  bu kullanıcıya daha önce firma tanımlanmış company: {company} ')


            # firmanın modullerine göre kullanıcıya yetki tanımlaması yapılır.
            modulYetkilendir(request,user,company)

            login(request, user)        # kullanıcı login olabildi. session içine user eklenir
            request.session.modified = True  # Update the session to ensure the user remains logged in
            time.sleep(1) # 1 saniye bekleme yapılır 
            request.session['company'] = company.id         # session içerisini company_id bilgisi company adında saklanır. sonraki sayfalarda bu kullanılır
            request.session['companyName'] = company.name   # companyname de session içerisinde tutulur.

            print("company sessiona a eklendi company:", request.session['company']   )
            # else browser session will be as long as the session  cookie time "SESSION_COOKIE_AGE"

            if saas.views.getSettings("toyu_adm_taskReg_bilgi",1):
                notification.views.send_sms(request,"5326179630",f" user:{user.username}  registerda telefon confirm tamamlandılogged in oldu ")
                #notification.views(request,"5322664250",f" user:{user.username}  registerda telefon confirm tamamlandılogged in oldu ")
 
            Logla(request,f"{user} taskmanagerregister tamamlandı logged in oldu .ilk gorev ekle sayfasına yönlendirildi")
            messages.success(request,"Başarıyla giriş yaptınız")
            print("request user",request.user)
            print("ilk gorev ekle sayfasına yönlendirilecek")
            
            return redirect("/gorevler/ilkgorevEkle")
            
        else:
            print("kod hatalı yada süresi geçmiş")
            messages.error(request,"Kod hatalı yada süresi geçmiş")
            Logla(request,f'Kod hatalı yada süresi geçmiş {user}')
            return redirect("/user/register")
    else:
        print("telefon confirm sayfası çalıştırılıyor")
        return render(request,"telephoneConfirm.html")
    




def taskmanagerRegister(request):

    #TODO: ip kontrolü yapılmalı. 3 dk içinde 3 den fazla kayıt olma durumunda engelleme yapılmalı

    if request.method == 'POST':
        telephone = request.POST.get("telephone").replace("(","").replace(")","").replace(".","").replace(" ","")[-10:]
        print(telephone)
        name = request.POST.get("name")
        surname = request.POST.get("surname")
        kosulKabul = request.POST.get("checkbox")
    
        if kosulKabul and name and surname and telephone:
            user = User.objects.filter(username = telephone)
            print(user)
            print("user count",user.count() )
            #########################################################################
            # reCAPTCHA doğrulamasını kontrol et
            # bunu için goole de ayarların yapılmış olması gerekiyor.
            # Gerekli key bilgileri setting dosyasına işlendi
            recaptcha_response = request.POST.get('g-recaptcha-response')
            ##### json data oluşturularak google dan bilgi alınız
            data = {
                'response': recaptcha_response,
                'secret': settings.RECAPTCHA_PRIVATE_KEY
            }
            resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result_json = resp.json()
            #########################################################################
                
            if result_json.get('success'):          # robot kontrolu yaptık
                print("robot değil")
                if user.count() == 1 :               # daha önce kullanıcı tanımlanmış ise
                    newUser = user[0]       # surecin bundan sonraki kısmında bu kullanıcı kullanılacak
                    if newUser.is_active == 0:      # kullanıcı tanımlanmış fakat aktif değilse
                        
                        newUser.employee.otp = str(random.randint(1000,9999))   #otp one time password
                        newUser.employee.otp_expiredate = datetime.datetime.now() + datetime.timedelta(minutes=3)
                        newUser.employee.save()
                        Logla(request,f'user:{newUser} OTP tekrar ayarlandı . kullanıcı daha önce tanımlanmış ')

                    else:
                        Logla(request,f'Telefon numarası daha önce aktif olmus {newUser.id} {telephone}')
                        messages.info(request,"Telefon numarası daha önce kullanılmış şifre resetleme yapabilirsiniz.")
                        return redirect('/user/passwordResetWithPhone')

                elif user.count() == 0:                           # kullanıcı ilk defa tanımlanıyor ise
                    try:
                        #createUsername(email,telephone,name,surname)
                        
                        newUser = User( username = telephone, is_active=0,first_name=name,last_name=surname)
                        newUser.save()
                        Logla(request,f'user:{newUser} eklendi active=0 ')

                        newUser.employee.telephone = telephone      # user ile employee tablosu onetoone bağlı
                        newUser.employee.otp = str(random.randint(1000,9999))   #otp one time password
                        newUser.employee.otp_expiredate = datetime.datetime.now() + datetime.timedelta(minutes=3)
                        newUser.employee.save()
                        Logla(request,f'user:{newUser} OTP ayarlandı ')

                        #TODO aldığı modul bilgisine göre register olurken onun yetkileri tanımlanmalı
                        # su an sadece tas management register ediliyor. momdul parametrik gelmeli....
                        # kullanıcı eklemesi yapılırken mmodule göre yetki verilecek yada yekti firmaya tanımlanacak ????

                        my_group = Group.objects.get(id=2)  # task_management_grp_perm isimli grup tanımlıdır.  Admin için bu tanımlanıyor.
                        my_group.user_set.add(newUser)
                        Logla(request,f'user:{newUser} Grup tanımlaması yapıldı ')

                    except Exception as e:
                        messages.error(request,"user tanımlamada hata : "+ str(e))
                        Logla(request,f'user tanımlamada hata: {str(e)} ')
                else:
                    Logla(request,f'tel:{telephone} çoklu kullanıcı var!!! function: taskmanagerRegister ')
                    messages.info(request,f'tel:{telephone} çoklu kullanıcı var!!! destek@toyu.app adresine mail atınız')

                # kullanıcı ilk defa da tanımlansa ara süreçten tekrar da girse aynı işlemler yapılır
                """if saas.views.getSettings("toyu_adm_taskReg_bilgi",1):
                    notification.views.send_sms(request,"5326179630",f"tasmanagerregister yeni kullanıcı {newUser.username}  kod gonderilecek ")
                    notification.views.send_sms(request,"5322664250",f"tasmanagerregister yeni kullanıcı {newUser.username}  kod gonderilecek ")"""

                notification.views.send_sms(request,telephone,f"TOYU doğrulama kodu: {newUser.employee.otp} ")
                Logla(request,f'user:{newUser} doğrulama kodu gönderildi tel:{newUser.employee.telephone} ')
                messages.info(request,"Doğrulama kodu gönderildi")  
                return redirect(f"/user/telephoneConfirm/{newUser.id}")
            else:
                print("robot algılandı")
                print(result_json)
                Logla(request,f'robot algılandı {result_json} ')
        else:
            messages.warning(request,"Lütfen bilgileri doldurup kullanım koşullarını kabul ediniz")
    
    
    return render(request,'taskmanagerRegister.html',{'site_key': settings.RECAPTCHA_PUBLIC_KEY})

def passwordResetWithPhone(request):
    if request.method == 'POST':
        telephone = request.POST.get("telephone").replace(".","").replace(" ","").replace("+","").replace("(","").replace(")","").replace("-","")
        if telephone[0] == "0":
            telephone = telephone
        else:
            telephone = "0"+telephone
        print(telephone)
        
        #########################################################################
        # reCAPTCHA doğrulamasını kontrol et
        # bunu için goole de ayarların yapılmış olması gerekiyor.
        # Gerekli key bilgileri setting dosyasına işlendi
        recaptcha_response = request.POST.get('g-recaptcha-response')
        ##### json data oluşturularak google dan bilgi alınız
        data = {
            'response': recaptcha_response,
            'secret': settings.RECAPTCHA_PRIVATE_KEY
        }
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result_json = resp.json()
        #########################################################################
        

        if result_json.get('success'):          # robot kontrolu yaptık
            
            user = User.objects.filter(username = telephone)
            if user.count() == 1:
                user = user[0]
                print(user, "active:" ,user.is_active)

                if user.is_active == 1:      # kullanıcı aktif ise
                    code = str(random.randint(1000,9999))
                    
                    user.employee.otp =  code  #otp one time password
                    user.employee.otp_expiredate = datetime.datetime.now() + datetime.timedelta(minutes=3)
                    user.employee.save()

                    print(code)
                
                    Logla(request,f'user:{user} şifre resetleme için  OTP tekrar ayarlandı . ')
                    notification.views.send_sms(request,telephone,f"TOYU şifre sıfırlama kodu: {user.employee.otp} ")
                    notification.views.whatsappMessage(request,telephone,f"TOYU şifre sıfırlama kodu: {user.employee.otp} ")
                    Logla(request,f'user:{user} şifre sıfırlama kodu gönderildi tel:{user.employee.telephone} ')
                    messages.info(request,"Şifre sıfırlama kodu gönderildi")
                    return redirect(f"/user/passwordResetWithPhoneConfirm/{user.id}")
                else:
                    messages.info(request,"Şifre sıfırlamada hata. Kullanıcı aktif değil kayıt işlemini tamamlayınız yada destek@toyu.app a mail atabilirsiniz")
                    return redirect('/user/simpleRegister')
            else:
                messages.info(request,"Telefon numarası daha önce kullanılmamış. Kayıt olup sistemi kullanabilir yada destek@toyu.app a mail atabilirsiniz")
                Logla(request,f'Telefon numarası daha önce kullanılmamış {telephone} yada birden fazla kullanıcı var ')
                return redirect('/user/simpleRegister')
        else:
            print("Robot algılandı")
            print(result_json)
            Logla(request,f'Robot algılandı {result_json} ')
                
    return render(request,'passwordResetWithPhone.html',{'site_key': settings.RECAPTCHA_PUBLIC_KEY})

def passwordResetWithPhoneConfirm(request,userid):

    if request.method == 'POST':

        #########################################################################
        # reCAPTCHA doğrulamasını kontrol et
        # bunu için goole de ayarların yapılmış olması gerekiyor.
        # Gerekli key bilgileri setting dosyasına işlendi
        recaptcha_response = request.POST.get('g-recaptcha-response')
        ##### json data oluşturularak google dan bilgi alınız
        data = {
            'response': recaptcha_response,
            'secret': settings.RECAPTCHA_PRIVATE_KEY
        }
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result_json = resp.json()
        #########################################################################
        

        if result_json.get('success'):          # robot kontrolu yaptık

            code= request.POST.get("code")
            user = User.objects.get(id = userid)

            if user.employee.otp == code and user.employee.otp_expiredate > datetime.datetime.now():       # kullanıcı doğrulandı
               
                Logla(request,f'password_reset_telefon code doğrulandı ilgili_user:{user.username}')
                password = str(random.randint(100000,999999))
                user.set_password(password)      # kullanıcı şifresi sıfırlanır
                user.save()

                Logla(request,f'password_reset_telefon sistem yeni password atadı ilgili_user:{user.username}')

                notification.views.send_sms(request,user.employee.telephone,f"Şifre güncellendi TOYU user:{user.username} password : {password} ")
                notification.views.whatsappMessage(request,user.employee.telephone,f"Şifre güncellendi TOYU user:{user.username} password : {password} ")
                Logla(request,f'password_reset_telefon password sms ile gonderildi ilgili_user:{user.username}')
                messages.success(request,"Şifre sıfırlandı")
                return redirect("/user/login")
            else:
                messages.error(request,"Kod hatalı yada süresi geçmiş")
                Logla(request,f"password_reset_telefon Kod hatalı yada süresi geçmiş ilgili_user:{user.username}")
                return redirect(f"/user/passwordResetWithPhone/")
        else:
            print("Robot algılandı")
            print(result_json)
            Logla(request,f'Robot algılandı {result_json} ')

    
    return render(request,"passwordResetTelephoneConfirm.html",{'site_key': settings.RECAPTCHA_PUBLIC_KEY})

        

def yetkiYok(request):

    return  render(request,'yetkiYok.html')


def loginPage(request):
    # POST ve GET methodları var.burada POST Kullanılıyor
    username = request.POST.get("username")
    password = request.POST.get("password")
    remember_me = request.POST.get("remember_me")
    
    if username :

        print(username)
        user = authenticate(request, password=password, username=username,is_active=1) # kullanıcı adı şifre doğru olsa bile kullanıcı aktif değilse login olamaz
        if user is None:
            messages.info(request,"Kullanıcı adı veya parola hatalı")
            Logla(request,f"{username} kullanıcı adı veya parola hatalı")
            return render(request,"login.html")
        
        login(request, user)        # kullanıcı login olabildi. session içine user eklenir
        Logla(request,f"user:{user} logged in")

        company = user.employee.company
        company_id = company.id                     # kullanıcının firma bilgisi alınır

        request.session['company'] = company_id         # session içerisini company_id bilgisi company adında saklanır. sonraki sayfalarda bu kullanılır
        request.session['companyName'] = company.name   # companyname de session içerisinde tutulur.
        

        if company.logo :           # firmanın logosu sisteme yüklenmiş ise bu da session a atılır
            request.session['companyLogoUrl'] = company.logo.url
            print(company.logo.url)
        
        if not remember_me:                     # remember_me seçilimi kontrol edilir.
            request.session.set_expiry(0)       # seçili değilse expire suresi 0 yapılarak browser kapatıldığında session bilgisinin silinmesi sağlanır
        else:
            # Varsayılan sürede kalıcı olacak
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30 gün
                      
        
        Logla(request,f"user:{user} session ayrları yapıldı")
        messages.success(request,"Başarıyla giriş yaptınız")
        
        #TODO: default açılış sayfasını ayarlardan değiştirebiliriz. bu özelliği ekleyelim. 
        """# kullanıcığı module göre login sonrası sayfa yonlendirmesi yapılıyor
        company = Company.objects.get(id = request.session['company'])
        companyModules = CompanyModules.objects.filter(company=company)
        for modulesRecond in companyModules:
            
            if modulesRecond.modules_id == 3:
                return redirect("/production/productionTaskListMy")
            if modulesRecond.modules_id == 1:
                return redirect("/gorevler/gorevListele/all")"""

        return redirect("/user/userList/all")
    
    return  render(request,'login.html')

    #return  render(request,'login_google.html')

def logoutPage(request):
    Logla(request,f"logoutPage Kullanıcı: {str(request.user)}  çıkış yapıtı")
    logout(request)
    return  redirect("/user/login")

def usernameCheck(username):
    # belirtilen kullanıcı adı sistemde mevcut mu kontrol edilir
    user = User.objects.filter(username=username)
    if user.count() > 0:
        return True
    else:
        return False
    
def usernameClean(username):
    # kullanıcı adı temizlenir. özel karakterler temizlenir
    replacements = (
        (" ", "_"),
        ("ç", "c"),
        ("Ç", "C"),
        ("ğ", "g"),
        ("Ğ", "G"),
        ("ı", "i"),
        ("İ", "I"),
        ("ö", "o"),
        ("Ö", "O"),
        ("ş", "s"),
        ("Ş", "S"),
        ("ü", "u"),
        ("Ü", "U")
    )

    for old, new in replacements:
        username = username.replace(old, new)
    return username

def createUsername(email,telephone,first_name,last_name):

    # öncelki emmail ile kullanıcı oluşturmada
    if email:   #email girilmiş mi kontrol edilir.
        if usernameCheck(email) == False: # email e user oluşturulmmuş mu kontrol edilir.
            return email
    
    # eğer email ile kullanıcı oluşturulamamış ise telefon numarası ile oluşturulur
    if telephone:
        if usernameCheck(telephone) == False:
            return telephone
    
    if first_name or last_name:
        username = first_name+last_name
        username = usernameClean(username) # kullanıcı adı temizlenir türkçe karakterler çıkartılır

        while True:
            if usernameCheck(username) == False:    # kullanıcı adı sistemde mevcut değilse bu kullanıcı adı kullanılır
                return username     
            else:                                   # kullanıcı adı sistemde mevcut ise random bir sayı eklenir tekrar kontrol edilir
                username = username+str(random.randint(100,999))
    
        
@login_required(login_url='/user/login/')
@permission_required('auth.add_user',login_url='/user/yetkiYok/')
def userAdd(request):
    form = RegisterForm(request.POST or None)
    
    if form.is_valid():
        
        #username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        telephone = form.cleaned_data.get("telephone")
        telephone2 = form.cleaned_data.get("telephone2")
        email = form.cleaned_data.get("email")
        sube = form.cleaned_data.get("sube")
        department = form.cleaned_data.get("department")
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        isAdmin = form.cleaned_data.get("isAdmin")

        company = Company.objects.get(id = request.session['company'])
        companyModules = CompanyModules.objects.filter(company=company)

        username = createUsername(email,telephone,first_name,last_name) # otomatik olarak username create edilir
        newUser = User( username = username,email=email,first_name=first_name,last_name=last_name)
        Logla(request,f"user:{username} eklendi ")

        newUser.set_password(password)
        newUser.save()
        Logla(request,f"user:{username} password tanımlandı ")

        #TODO: firmanın sahip olduğu modullere gore kullanıcıya yetki tanımlanmalı. fakat bu admindeğil noraml kullanıcı
        """
        1	company_admin
        2	task_management_grp_perm
        3	field_operations_grp_perm
        4	production_management_grp_perm
        5	project_management_grp_perm
        6	problem_management_grp_perm
        7	task_management_grp_perm_normal_user
        8	production_management_grp_perm_normal_user
        """
        for modulesRecond in companyModules:
            if modulesRecond.modules_id == 1: # 1 görev yonetimi
                my_group = Group.objects.get(id=7)  
                # id : 2 task_management_grp_perm isimli grup tanımlıdır.  Admin için bu tanımlanıyor.
                # id : 7 task_management_grp_perm_normal_user için kullanılıyor.
                my_group.user_set.add(newUser)
                my_group.save()
                Logla(request,f"user:{username} yetkiler tanımlandı ")
            if modulesRecond.modules_id == 3: # üretim yonetimi
                admin_grp = Group.objects.get(id=4)  # üretim yönetimi modulu için admin
                normal_grp = Group.objects.get(id=8)  # admin olmayan normal kullanıcılar için

                if isAdmin:
                    my_group = Group.objects.get(id=4)  # üretim yönetimi modulu için admin
                else:
                    my_group = Group.objects.get(id=8)  # admin olmayan normal kullanıcılar için

                my_group.user_set.add(newUser)
                my_group.save()
                Logla(request,f"user:{username} yetkiler tanımlandı ")
        newEmployee = Employee.objects.get(user = newUser)
        newEmployee.department= Departments.objects.get(title=department)
        Logla(request,f"user:{username} departman tanımlandı ")

        #TODO: firmanın subesi olmalı ve bu eklenmeli
        newEmployee.sube_id = sube
        newEmployee.telephone = telephone
        newEmployee.telephone2 = telephone2
        newEmployee.isAdmin = isAdmin
        newEmployee.company_id = request.session['company']
        Logla(request,f"user:{username} sube,telefon ve Company!!! tanımlandı ")

        try:
            
            newEmployee.save()
            
            Logla(request,f"user:{username} user_id:{newUser.id} ayarları yapıldı ")
            return redirect("/user/userList/all")
        except:
            
            newUser.delete() # employee save edilemezse kullanıcının da silinmesi gerekir
            messages.warning(request,"!!! HATA girdiğiniz bilgilerde bir problem var")
    
    context = {'form':form}
    return  render(request,'userAdd.html',context)

@login_required(login_url='/user/login/')
@permission_required('auth.add_user',login_url='/user/yetkiYok/')
def userSetAdmin(request,id,isAdmin):
    
    company = Company.objects.get(id = request.session['company'])
    companyModules = CompanyModules.objects.filter(company=company)
    user = User.objects.get(id=id)

    if company.id == 1 : # teknolikya admini ise firma olarak ayar yaptığımız kullanıcının firması secilir
        company = user.employee.company
        companyModules = CompanyModules.objects.filter(company=company)

    print(company)

    if isAdmin == "True":
        user.employee.isAdmin = False
        user.employee.save()
        Logla(request,f"user:{user} adminlikten çıkarıldı ")
    else:
        user.employee.isAdmin = True
        user.employee.save()
        Logla(request,f"user:{user} admin yapıldı ")


    for modulesRecond in companyModules:
        if modulesRecond.modules_id == 1: # 1 görev yonetimi
            my_group = Group.objects.get(id=7)  
            # id : 2 task_management_grp_perm isimli grup tanımlıdır.  Admin için bu tanımlanıyor.
            # id : 7 task_management_grp_perm_normal_user için kullanılıyor.
            my_group.user_set.add(user)
            my_group.save()
            Logla(request,f"user:{user} yetkiler tanımlandı ")
        if modulesRecond.modules_id == 3: # üretim yonetimi

            adminGrup = Group.objects.get(id=4)  # üretim yönetimi modulu için admin
            normalGrup = Group.objects.get(id=8)  # admin olmayan normal kullanıcılar için

            if user.employee.isAdmin:
                adminGrup.user_set.add(user)
                normalGrup.user_set.remove(user)
                messages.success(request,"Admin yapıldı")
                print("admin yapıldı")
            else:
                adminGrup.user_set.remove(user)
                normalGrup.user_set.add(user)
                messages.success(request,"Adminlikten çıkarıldı")
                print("adminlikten çıkarıldı")

            adminGrup.save()
            normalGrup.save()

            Logla(request,f"user:{user} yetkiler tanımlandı ")
    return redirect("/user/userList/all")

@login_required(login_url='/user/login/')
@permission_required('auth.view_user',login_url='/user/yetkiYok/')
def userView(request,id):
    user = get_object_or_404(User,id=id)
    wf = Workflow.objects.filter(completed_user_id=user.id)
    hakedis = Hakedis.objects.filter(user_id=user.id)

    ####################################
    dd=[]
    
    reservation = Hakedis.objects.filter(user= user)
    
    
    for ay in range(1,13) :
        #hak = Hakedis.objects.filter(user_id=1).filter(created_date__year=datetime.datetime.now().year,created_date__month=ay).aggregate(Sum('adet'))['adet__sum']
        if ay == 12:
            sDate = str(datetime.datetime.now().year)+"-"+str(ay)+"-15"
            eDate = str(datetime.datetime.now().year+1)+"-"+str(1)+"-15"
        else:
            sDate = str(datetime.datetime.now().year)+"-"+str(ay)+"-15"
            eDate = str(datetime.datetime.now().year)+"-"+str(ay+1)+"-15"

        hak = Hakedis.objects.filter(user=user).filter(created_date__gt=sDate,created_date__lt=eDate).aggregate(Sum('adet'))['adet__sum']
        dd.append( [ay, hak])
        

    my_array = np.array(dd)
    df = pd.DataFrame(my_array, columns = ['Ay','Hakedis'])
  
    #fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task",height=700,width=1900,opacity =0.5)
    fig = px.bar(df, x='Ay', y='Hakedis')

    #fig.update_yaxes(autorange="reversed")


    # Setting layout of the figure.
    layout = {
        'title': 'Title of the figure',
        'xaxis_title': 'X',
        'yaxis_title': 'Y',
        'height': 400,
        'width': 700,
    }

    plot_div = plot({'data': fig, 'layout': layout}, output_type='div')
  
    ####################################

    return  render(request,'userView.html',{'user':user,'wf':wf,'hakedis':hakedis,'plot_div': plot_div})

#@login_required(login_url='/user/login/')
@permission_required('auth.view_user',login_url='/user/yetkiYok/')
def userList(request,ap="all"):

    userid = request.POST.get("hidden") # password değişikliği için 
  
    if userid:
        if request.POST.get("inputPassword1") != "" and request.POST.get("inputPassword1") == request.POST.get("inputPassword2") :
            user = get_object_or_404(User,id=userid)
            user.set_password( request.POST.get("inputPassword1") )
            user.save()
            messages.success(request,"Şifre değiştirildi")
        else:
            messages.warning(request,"Şifreler aynı değil tekrar deneyin")
    
    keyword = request.GET.get("keyword")


    ############################  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if request.user.is_superuser:       # superuser ise tüm kullanıcılar listelenir
        if keyword:
            users = User.objects.filter(username__contains = keyword).order_by('-date_joined')
        else: 
            if ap == "all":
                users = User.objects.all().order_by('-date_joined')
            elif ap == "active":
                users = User.objects.filter(is_active = True).order_by('-date_joined')
            elif ap == "pasive":
                users = User.objects.filter(is_active = False).order_by('-date_joined')
            elif ap == "yeni":
                users = User.objects.filter(is_active = True).order_by('-date_joined')
            elif ap == "eski":
                users = User.objects.filter(is_active = True).order_by('date_joined')
    ############################################
    else:                               # müşterilerden her hangi biri ise sadece kendi müşterileri listeler
        if keyword:
            users = User.objects.filter(username__contains = keyword,id__in = Employee.objects.values_list('user_id',flat=True).filter(company_id=request.session['company']) ).order_by('-date_joined')
        else:
            users = User.objects.filter(id__in = Employee.objects.values_list('user_id',flat=True).filter(company_id=request.session['company']) ).order_by('-date_joined')

    paginator = Paginator(users, 50) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    return  render(request,'userList.html',{'page_obj':page_obj})



   

@login_required(login_url='/user/login/')
@permission_required('auth.change_user',login_url='/user/yetkiYok/')
def userUpdate(request,id):
    #TODO kullanıcı güncellemede form bilgilerinin tamamına erişemedim. form ile model arası bir uyumsuzluk olabilir
    # güncelleme için farklı bir form tanımlayarak kısıtlı verilerle güncelleme yapılıyor
    # password güncellemesi için  ayrı bir buton koyalım

    user = get_object_or_404(User,id=id)
    employee = get_object_or_404(Employee,user=user,company_id=request.session['company'])
    print( user)
    #form = RegisterForm(request.POST or None, request.FILES or None,instance=user)

    form = UserUpdateForm(request.POST or None, request.FILES or None,instance=user)
    emp_form = EmployeeUpdateForm(request.POST or None, request.FILES or None,instance=employee)

    if form.is_valid() and emp_form.is_valid() :
        form.save()
        emp_form.save()

        #TODO: isAdmin bilgisine göre güncelleme yapılmalı.

        messages.success(request,"kullanıcı güncellendi")
        Logla(request,f"kullanıcı güncellendi user_id:{id} username:{user.username}")
        return redirect("/user/userList/all")
    
    return  render(request,'userUpdate_v2.html',{'form':form,'emp_form':emp_form})


@login_required(login_url='/user/login/')
def updateMyProfile(request):
    # id bilgisini fonksiyon dışarıdan almmaz . kullanıcının session bilgisi içindeki id kendi idsidir.
    
    user = get_object_or_404(User,id=request.user.id)
    employee = get_object_or_404(Employee,user=user)
    #form = RegisterForm(request.POST or None, request.FILES or None,instance=user)

    form = UserUpdateForm(request.POST or None, request.FILES or None,instance=user)
    emp_form = EmployeeUpdateForm(request.POST or None, request.FILES or None,instance=employee)

    if form.is_valid() and emp_form.is_valid() :
        form.save()
        emp_form.save()
        messages.success(request,"kullanıcı güncellendi")
        Logla(request,f"kullanıcı güncellendi user_id:{id} username:{user.username}")
        return redirect("/user/userlist/all")
    
    return  render(request,'userUpdate_v2.html',{'form':form,'emp_form':emp_form})


@login_required(login_url='/user/login/')
def ChangeMyPassword(request):
    print(request.user.id,"kullanıcısının şifresi değişecek")
    user = get_object_or_404(User,id=request.user.id)

    form = ChangePassword(request.POST or None)
    

    if form.is_valid() :
        password = form.cleaned_data.get("password")
        print(password)
        user.set_password(password)
        user.save()
        messages.success(request,"kullanıcı şifresi güncellendi")
        Logla(request,str(user) + " kullanıcısı şifresini değiştirdi")
        #TODO: kullanıdığı module göre yönlendirme yapılacak. yetkiye göre dashboard ekranına da gidebilir
        return redirect("/production/productionTaskListMy")
    
    return  render(request,'userChangePassword.html',{'form':form})




@login_required(login_url='/user/login/')
@permission_required('auth.change_user',login_url='/user/yetkiYok/')
def userChangePassword(request,id):
   
    user = get_object_or_404(User,id=id)
  
    form = ChangePassword(request.POST or None)
    #TODO: şifre değişikliğiini superuser yada ilgili firmanın

    if form.is_valid() :
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.is_active = 1
        user.save()
        messages.success(request,"kullanıcı şifresi güncellendi")
        Logla(request,f"kullanıcı password değişti  user_id:{id} username:{user.username}")

        #########################################
        login(request, user)
        #company = Company.objects.get(user=user)
        company = user.employee.company
        company_id = company.id                     # kullanıcının firma bilgisi alınır
        request.session['company'] = company_id         # session içerisini company_id bilgisi company adında saklanır. sonraki sayfalarda bu kullanılır
        request.session['companyName'] = company.name   # companyname de session içerisinde tutulur.
        if company.logo :                               # firmanın logosu sisteme yüklenmiş ise bu da session a atılır
            request.session['companyLogoUrl'] = company.logo.url
            print(company.logo.url)
        #########################################
            

        notification.views.send_sms(request,user.employee.telephone,f"TOYU şifreniz değişti username:{user.username} pass:{password} ")

        return redirect("/gorevler/gorevListele/all")
    
    return  render(request,'userChangePassword.html',{'form':form})

@login_required(login_url='/user/login/')
@permission_required('auth.delete_user',login_url='/user/yetkiYok/')
def userDelete(request,id):
    print("silinecek id:",id)
    user = get_object_or_404(User,id=id)
    username = user.username
    if user :
        try:
            user.delete()
            messages.success(request,"Kullanıcı silindi")
            Logla(request,f"kullanıcı silindi user_id:{id} username:{username}")
        except Exception as e:
            messages.warning(request,f"Kullanıcı silinemedi hata: {e}")
            Logla(request,f"kullanıcı silinemedi user_id:{id} username:{username}")
    else:
        messages.success(request,"Kullanıcı bulunamadı!!!!!!")
    return  redirect("/user/userList/all")

@login_required(login_url='/user/login')
@permission_required('user.change_user',login_url='/user/yetkiYok/')
def userYetki(request,id,islem,perm):
    if islem == 'listele':
        user = get_object_or_404(User,id=id)
        p_list = Permission.objects.all()
        user_p_list = Permission.objects.filter(Q(user=user))
        
        if user :

            return  render(request,'userPermissionList.html',{'p_list':p_list,'user_p_list':user_p_list,'userid':id,'user':user})
            
        else:
            messages.success(request,"Kullanıcı bulunamadı!!!!!!")
        return  redirect("/user/userlist/all")
    elif islem == "add":
        permission = Permission.objects.get(codename=perm)
        user = User.objects.get(id=id)
        user.user_permissions.add(permission)
        return redirect(request.META['HTTP_REFERER'])
        
    elif islem == "remove":
        permission = Permission.objects.get(codename=perm)
        user = User.objects.get(id=id)
        user.user_permissions.remove(permission)
        return redirect(request.META['HTTP_REFERER'])



@login_required(login_url='/user/login/')
@permission_required('user.view_logging',login_url='/user/yetkiYok/')
def logView(request):


    """    keyword = request.GET.get("keyword")
        if keyword:
            loglar = Logging.objects.filter(aciklama__contains = keyword).order_by('date') | Logging.objects.filter(log_type__contains=keyword).order_by('date')
        else:
            loglar = Logging.objects.filter(date__gt=(datetime.date.today() - datetime.timedelta(days=7))).order_by('-date')

        page = request.GET.get('page', 1)   

        paginator = Paginator(loglar, 10)
        try:
            logs = paginator.page(page)
        except PageNotAnInteger:
            logs = paginator.page(1)
        except EmptyPage:
            logs = paginator.page(paginator.num_pages)
    """
    lines=[]
    with open("log.txt") as logfile:
        loglar = logfile.readlines()

        keyword = request.GET.get("keyword")
        if keyword:
            
            for log in loglar:
                if keyword in log:
                    lines.append([log[0:19], log[27:]])
        else:
            for log in loglar:
                lines.append([log[0:19], log[27:]])



    return  render(request,"loglar.html",{'lines':lines})




def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            print("----"+associated_users)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password_reset_email.txt"
                    c = {
                    "email":user.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'info@toyu.app' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password_reset.html", context={"password_reset_form":password_reset_form})

# Nazımdan Not: denizim ekledikleri güncellenecek. conflict vardı. denizim ekledğinde 1010. satır sonraı log view yoktu
@login_required(login_url='/user/login/')
#@permission_required('gorevler.add_gorevler',login_url='/user/yetkiYok/')
def departmentAdd(request):
    
    form = DepartmentForm(request.POST or None)
    if form.is_valid():  
        form.save()
        return redirect("/user/departmentList")
    
    return render(request,'departmentAdd.html',{"form":form})


@login_required(login_url='/user/login/')
def departmentList(request):
    departments = Departments.objects.all()

    return render(request,"departmentList.html",{"departments":departments})

@login_required(login_url='/user/login/')
def departmentDelete(request, id):
    department = get_object_or_404(Departments, id=id)
    try:
        department.delete()
    except:
        messages.warning(request,"bağlı kullanıcılar var")
    return redirect("/user/departmentList")

@login_required(login_url='/user/login/')
@permission_required('auth.change_user',login_url='/user/yetkiYok/')
def departmentUpdate(request,id):
    
    department = get_object_or_404(Departments,id=id)
    
    print( department)
    #form = RegisterForm(request.POST or None, request.FILES or None,instance=user)

    form =DepartmentForm(request.POST or None, request.FILES or None,instance=department)
    

    if form.is_valid():
        form.save()
        
        messages.success(request,"departman güncellendi")
        Logla(request,f"departman güncellendi departman_no:{department.department_number} departman:{department.title}")
        return redirect("/user/departmentList")
    
    return  render(request,'departmentUpdate.html',{'form':form})


@login_required(login_url='/user/login/')
@permission_required('user.log_listeleme',login_url='/user/yetkiYok/')
def logViewText(request):
    filtrelenmis_satirlar = []

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        keyword = request.POST.get('keyword')

        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

            print(start_date,end_date,keyword)
            # Log dosyasını açalım
            with open('log.txt', 'r') as log_dosyasi:
                for satir in log_dosyasi:
                    # Satırdaki tarih bilgisini alalım
                    tarih_bilgisi = satir.split(" ")[0]
                    # Tarih bilgisini datetime formatına dönüştürelim
                    try:
                        tarih = datetime.datetime.strptime(tarih_bilgisi, '%Y-%m-%d')
                    except ValueError:
                        # Tarih formatı hatalıysa satırı atlayalım
                        continue
                    # Tarih aralığında olup olmadığını kontrol edelim
                    if start_date <= tarih <= end_date:
                        # Aranacak içeriği satırda arayıp bulalım
                        if keyword:
                            if keyword in satir:
                                # Filtrelenen satırı listeye ekleyelim
                                filtrelenmis_satirlar.append(satir)
                            else:
                                continue
                        else:
                            filtrelenmis_satirlar.append(satir)
        else:
              with open('log.txt', 'r') as log_dosyasi:
                for satir in log_dosyasi:

                    if keyword:
                        if keyword in satir:
                            # Filtrelenen satırı listeye ekleyelim
                            filtrelenmis_satirlar.append(satir)
                        else:
                            continue
                    else:
                        filtrelenmis_satirlar.append(satir)
                
    else: # ilk girişte çalışır
        with open('log.txt', 'r') as log_dosyasi:
            lines = log_dosyasi.readlines()
            filtrelenmis_satirlar= lines[-500:]


    return  render(request,"loglar_text.html",{'filtrelenmis_satirlar':filtrelenmis_satirlar})



@login_required(login_url='/user/login/')
@permission_required('user.log_listeleme',login_url='/user/yetkiYok/')
def logViewSms(request):
    filtrelenmis_satirlar = []

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        keyword = request.POST.get('keyword')

        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

            print(start_date,end_date,keyword)
            # Log dosyasını açalım
            with open('log.txt', 'r') as log_dosyasi:
                for satir in log_dosyasi:
                    # Satırdaki tarih bilgisini alalım
                    tarih_bilgisi = satir.split(" ")[0]
                    # Tarih bilgisini datetime formatına dönüştürelim
                    try:
                        tarih = datetime.datetime.strptime(tarih_bilgisi, '%Y-%m-%d')
                    except ValueError:
                        # Tarih formatı hatalıysa satırı atlayalım
                        continue
                    # Tarih aralığında olup olmadığını kontrol edelim
                    if start_date <= tarih <= end_date:
                        # Aranacak içeriği satırda arayıp bulalım
                        if keyword:
                            if keyword in satir:
                                # Filtrelenen satırı listeye ekleyelim
                                filtrelenmis_satirlar.append(satir)
                            else:
                                continue
                        else:
                            filtrelenmis_satirlar.append(satir)
        else:
              with open('log.txt', 'r') as log_dosyasi:
                for satir in log_dosyasi:

                    if keyword:
                        if keyword in satir:
                            # Filtrelenen satırı listeye ekleyelim
                            filtrelenmis_satirlar.append(satir)
                        else:
                            continue
                    else:
                        filtrelenmis_satirlar.append(satir)
                
    else: # ilk girişte çalışır
        with open('logSms.txt', 'r') as log_dosyasi:
            filtrelenmis_satirlar = log_dosyasi.readlines()


    return  render(request,"loglar_text.html",{'filtrelenmis_satirlar':filtrelenmis_satirlar})

@login_required(login_url='/user/login/')
def moduleDocs(request):
    return render(request,"moduleDocs.html")