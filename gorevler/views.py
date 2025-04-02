from django.shortcuts import render

from notification.views import whatsappMessage
from .forms import GorevForm, GorevTamamla ,GorevNotuForm,GorevIlkForm,GorevStatuForm,ReminderForm,DuzenliGorevForm
from .models import Gorevler,GorevlerStatu,GorevNotu,Reminder,DuzenliGorevTanim
from saas.models import Company

from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, response
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.contrib import messages
from user.views import Logla
import datetime
from datetime import timedelta
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.db.models import F,Q
from django.contrib.auth.models import User
import calendar

#TODO yetkileri güncellemek gerekiyor
aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
color = ["blue","green","red","cyan","magenta","yellow","black"]


@login_required(login_url='/user/login/')
@permission_required('gorevler.add_gorevler',login_url='/user/yetkiYok/')
def duzenliGorevTanimla(request):
    form = DuzenliGorevForm(request.session['company'],request.POST or None,request.FILES or None)
    if form.is_valid():
        duzenliGorev = form.save(commit=False)
        duzenliGorev.created_date = datetime.datetime.now()
        duzenliGorev.company_id = request.session['company']
        duzenliGorev.created_user = request.user
        duzenliGorev.save()
        messages.success(request,"Düzenli görev tanımlandı")
        Logla(request,f"Düzenli görev tanımlandı tanim_id:{duzenliGorev.id}")
        return redirect("/gorevler/duzenliGorevListele")

    return render(request,"gorevEkle.html",{'form':form})

@login_required(login_url='/user/login/')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def duzenliGorevListele(request):
    duzenliGorevler = DuzenliGorevTanim.objects.filter(company_id=request.session['company']).order_by('is_active')
    
    paginator = Paginator(duzenliGorevler, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request,"duzenliGorevListele.html",{'page_obj':page_obj})

@login_required(login_url='/user/login/')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def duzenliGorevGuncelle(request,id):
    duzenliGorev = get_object_or_404(DuzenliGorevTanim,id=id)
    form = DuzenliGorevForm(request.session['company'],request.POST or None,instance=duzenliGorev)
    if form.is_valid():
        duzenliGorev = form.save(commit=False)
        duzenliGorev.save()
        messages.success(request,"Düzenli görev güncellendi")
        Logla(request,f"Düzenli görev güncellendi tanim_id:{duzenliGorev.id}")
        return redirect("/gorevler/duzenliGorevListele")

    return render(request,"gorevEkle.html",{'form':form})

@login_required(login_url='/user/login/')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def duzenliGorevSil(request,id):
    duzenliGorev = get_object_or_404(DuzenliGorevTanim,id=id)
    duzenliGorev.delete()
    messages.success(request,"Düzenli görev silindi")
    Logla(request,f"Düzenli görev silindi tanim_id:{duzenliGorev.id}")
    return redirect("/gorevler/duzenliGorevListele")

@login_required(login_url='/user/login/')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def duzenliGorevGoster(request,id):
    duzenliGorev = get_object_or_404(DuzenliGorevTanim,id=id)
    return render(request,"duzenliGorevGoster.html",{'duzenliGorev':duzenliGorev})

@login_required(login_url='/user/login/')
@permission_required('gorevler.add_gorevler',login_url='/user/yetkiYok/')
def gorevEkle(request):

    form = GorevForm(request.session['company'],request.POST or None,request.FILES or None)
    #formReminder = ReminderForm(request.POST or None)

    #TODO: GÖREV EKLERKEN DOSYAYI ALMIYORU ANCAK GÜNCELLEMEDE ALIYOR

    if request.method == "POST"  :
        if form.is_valid() :  #  and formReminder.is_valid():
            gorev = form.save(commit=False)
            gorev.created_date  = datetime.datetime.now()
            gorev.company_id    = request.session['company']
            gorev.open_user     = request.user
            smsGonder = form.cleaned_data.get("smsGonder")
            gorev.save()

            # reminder = formReminder.save(commit=False)
            # reminder.gorev = gorev
            # reminder.created_date = datetime.datetime.now()
            # reminder.open_user = request.user
            # reminder.save()
            if smsGonder == "True"  and getSettings("gorev_sms_bilgilendir",request.session["company"]) and gorev.responsible_user.employee.telephone:
            
                scheme = request.is_secure() and "https" or "http"
                hostname =  f'{scheme}://{request.get_host()}/'

                if gorev.start_date :
                    startDate = gorev.start_date.strftime("%Y%m%d")
                else:
                    startDate = ""
                
                if gorev.deadline:
                    endDate = gorev.deadline.strftime("%Y%m%d")
                else:
                    endDate = ""

                #gsm_message = f"Yeni Görev : \"{gorev.title}\"  baş-bit:{startDate}{endDate}  {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
                gsm_message = f"Görev \"{smsTitle(gorev.title)}\" {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
                send_sms(request,gorev.responsible_user.employee.telephone,gsm_message)
                whatsappMessage(request,gorev.responsible_user.employee.telephone,gsm_message)
                Logla(request,f"{gorev.responsible_user.employee.telephone} numaralı telefona sms gönderildi gorev_id:{gorev.id}")

            messages.info(request," task tanımlandı")
            Logla(request,f"Görev eklendi gorev_id:{gorev.id}")
            return redirect("/gorevler/gorevListele/aktif")


    return  render(request,'gorevEkle.html',{'form':form})  #,"formReminder":formReminder}) 

"""
@login_required(login_url='/user/login/')
@permission_required('gorevler.add_gorevler',login_url='/user/yetkiYok/')
def gorevEkle(request):

    gorevler = Gorevler.objects.filter(open_user=request.user,company_id=request.session['company'])
  
    form = GorevForm(request.session['company'],request.POST or None,request.FILES or None)
    formReminder = ReminderForm(request.POST or None)

    #TODO: GÖREV EKLERKEN DOSYAYI ALMIYORU ANCAK GÜNCELLEMEDE ALIYOR

    if request.method == "POST"  :
        if form.is_valid() and formReminder.is_valid():
            gorev = form.save(commit=False)
            gorev.created_date  = datetime.datetime.now()
            gorev.company_id    = request.session['company']
            gorev.open_user     = request.user

            smsGonder = form.cleaned_data.get("smsGonder")
            
            gorev.save()

            reminder = formReminder.save(commit=False)
            reminder.gorev = gorev
            reminder.created_date = datetime.datetime.now()
            reminder.open_user = request.user
            reminder.save()


           
            if smsGonder == "True"  and getSettings("gorev_sms_bilgilendir",request.session["company"]) and gorev.responsible_user.employee.telephone:
            
                scheme = request.is_secure() and "https" or "http"
                hostname =  f'{scheme}://{request.get_host()}/'

                if gorev.start_date :
                    startDate = gorev.start_date.strftime("%Y%m%d")
                else:
                    startDate = ""
                
                if gorev.deadline:
                    endDate = gorev.deadline.strftime("%Y%m%d")
                else:
                    endDate = ""

                #gsm_message = f"Yeni Görev : \"{gorev.title}\"  baş-bit:{startDate}{endDate}  {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
                gsm_message = f"Görev \"{smsTitle(gorev.title)}\" {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
                send_sms(request,gorev.responsible_user.employee.telephone,gsm_message)
                #send_whatsapp(request,gorev.responsible_user.employee.telephone,gsm_message)
                whatsappMessage(request,gorev.responsible_user.employee.telephone,gsm_message)
                Logla(request,f"{gorev.responsible_user.employee.telephone} numaralı telefona sms gönderildi gorev_id:{gorev.id}")

            messages.info(request," task tanımlandı")
            Logla(request,f"Görev eklendi gorev_id:{gorev.id}")
            return redirect("/gorevler/gorevListele/aktif")


    return  render(request,'gorevEkle.html',{'form':form,"formReminder":formReminder}) 
    
"""


def smsTitle(title):
    if len(title) > 15:
        title = title[:15]
    return title

#@login_required(login_url='/user/login/')
#@permission_required('gorevler.add_gorevler',login_url='/user/yetkiYok/')
def ilkgorevEkle(request):
    print("ilk gorev ekle------")
    print(request.session['company'])
    print(request.user) 

    form = GorevIlkForm(request.POST or None,request.FILES or None) # ilk görev tanımlanacaksa bu form kullanılır

    if request.method == "POST"  :
        if form.is_valid():
            gorev = form.save(commit=False)
            gorev.created_date  = datetime.datetime.now()
            gorev.company_id    = request.session['company']
            gorev.open_user     = request.user
            gorev.responsible_user = request.user
            gorev.save()

            if getSettings("gorev_sms_bilgilendir",request.session["company"]) and gorev.responsible_user.employee.telephone:
            
                scheme = request.is_secure() and "https" or "http"
                hostname =  f'{scheme}://{request.get_host()}/'
                if gorev.start_date :
                    startDate = gorev.start_date.strftime("%Y%m%d")
                else:
                    startDate = ""
                
                if gorev.deadline:
                    endDate = gorev.deadline.strftime("%Y%m%d")
                else:
                    endDate = ""
                    
                #gsm_message = f"Yeni Görev : \"{gorev.title}\"  baş-bit:{startDate}-{endDate}  {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
                gsm_message = f"Görev \"{smsTitle(gorev.title)}\" {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
                send_sms(request,gorev.responsible_user.employee.telephone,gsm_message)
                Logla(request,f"{gorev.responsible_user.employee.telephone} numaralı telefona sms gönderildi gorev_id:{gorev.id}")
                
            messages.info(request,"İlk görev tanımlandı")
            Logla(request,f"İlk görev eklendi gorev_id:{gorev.id}")
            return render(request,"smsYonlendirme.html",{'gorev':gorev})

    return  render(request,'ilkGorevEkle.html',{'form':form,'user':request.user})


@login_required(login_url='/user/login/')
def gorevSmsGonder(request,gorev_id):
    gorev = get_object_or_404(Gorevler,id=gorev_id)

    scheme = request.is_secure() and "https" or "http"
    hostname =  f'{scheme}://{request.get_host()}/'
    startDate = gorev.start_date.strftime("%Y%m%d")
    endDate = gorev.deadline.strftime("%Y%m%d")
    #gsm_message = f"Yeni Görev : \"{gorev.title}\"  baş-bit:{startDate}-{endDate}  {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
    gsm_message = f"Görev \"{smsTitle(gorev.title)}\" {hostname}gorevler/taskViewWithSecret/"+ str(gorev.id) +"/"+gorev.secret
    send_sms(request,gorev.responsible_user.employee.telephone,gsm_message)
    
    Logla(request,f"{gorev.responsible_user.employee.telephone} numaralı telefona TEKRAR sms gönderildi gorev_id:{gorev.id}")
    messages.info(request,"Sms TEKRAR gönderildi")

    return render(request,"smsYonlendirme.html",{'gorev':gorev})

@login_required(login_url='/user/login/')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def gorevListele(request,ap="all"):

    try:
        company = Company.objects.get(id=request.session['company'])
    except:
        messages.error(request,"Görev listelemede Firma bilgisi bulunamadı")
        return redirect("/user/login")
    
    # firmaya ait görev statuleri alınır. default statuler dışında olanlar listelenir.
    # filrteleme yaparken bu statuler kullanılır
    gorevStatus = GorevlerStatu.objects.filter(company_id=request.session['company']).exclude(id__in=[1,2,3,4,5])

    duzenliGorevler = Gorevler.objects.filter(scheduledTask__isnull=False,closed_date__isnull=True,company_id=request.session['company']).order_by('deadline')
    
    #acık görevler içinde arama yapılır
    keyword = request.GET.get("keyword")
    if keyword:
        gorevler = Gorevler.objects.filter(title__contains = keyword,company_id=request.session['company']).filter(closed_date=None).filter(proje_id__isnull=True)
        
        return  render(request,'gorevListele.html',{'gorevler':gorevler})    

    if ap == "pasif":
        actigimGorevler = Gorevler.objects.filter(open_user=request.user,closed_date__isnull=False,company_id=request.session['company']).filter(proje_id__isnull=True)
        gorevlerim = Gorevler.objects.filter(responsible_user=request.user,closed_date__isnull=False,company_id=request.session['company']).filter(proje_id__isnull=True)
        
    elif ap == "aktif":
        actigimGorevler = Gorevler.objects.filter(open_user=request.user,closed_date__isnull = True,company_id=request.session['company']).filter(proje_id__isnull=True)
        gorevlerim = Gorevler.objects.filter(responsible_user=request.user,closed_date__isnull=True,company_id=request.session['company']).filter(proje_id__isnull=True)

    elif ap == "baslangicTarihi":
        #aşağıdaki iki satırda sıralama yapılırken hata alınıyor. ORM sorgusunile ilgili sorun yaşandı.
        #actigimGorevler = Gorevler.objects.filter(open_user=request.user,closed_date__isnull = True,company_id=request.session['company']).order_by('created_date')
        #gorevlerim = Gorevler.objects.filter(responsible_user=request.user,closed_date__isnull = True,company_id=request.session['company']).order_by('created_date')

        # çözüm olark chatgpt nin önerisinin dışında sıralama yapılırken sorted fonksiyonu kullanıldı
        actigimGorevler = Gorevler.objects.filter(open_user=request.user, closed_date__isnull=True, company_id=request.session['company']).filter(proje_id__isnull=True)
        actigimGorevler = sorted(actigimGorevler, key=lambda x: x.created_date)

        gorevlerim = Gorevler.objects.filter(responsible_user=request.user,closed_date__isnull = True,company_id=request.session['company']).filter(proje_id__isnull=True)
        gorevlerim = sorted(gorevlerim, key=lambda x: x.created_date)

    elif ap == "planlananTarih":
        actigimGorevler = Gorevler.objects.filter(open_user=request.user,closed_date__isnull = True,company_id=request.session['company']).order_by('deadline').filter(proje_id__isnull=True)
        gorevlerim = Gorevler.objects.filter(responsible_user=request.user,closed_date__isnull = True,company_id=request.session['company']).order_by('deadline').filter(proje_id__isnull=True)
    
    elif ap == "all":
        actigimGorevler = Gorevler.objects.filter(open_user=request.user,company_id=request.session['company']).filter(proje_id__isnull=True)
        gorevlerim = Gorevler.objects.filter(responsible_user=request.user,company_id=request.session['company']).filter(proje_id__isnull=True)
    
    else:
        # burası firmanın custom statu tanımlaması varsa ona göre çalışır
        # statu id si buraya gelir
        try:
            statu = int(ap)     # buraya gelen deger statu idsi olacak
            actigimGorevler = Gorevler.objects.filter(open_user=request.user,company_id=request.session['company'],statu_id=statu).filter(proje_id__isnull=True)
            gorevlerim = Gorevler.objects.filter(responsible_user=request.user,company_id=request.session['company'],statu_id=statu).filter(proje_id__isnull=True)

        except:
            messages.error(request,"Hatalı parametre")
            actigimGorevler = Gorevler.objects.filter(open_user=request.user,company_id=request.session['company']).filter(proje_id__isnull=True)
            gorevlerim = Gorevler.objects.filter(responsible_user=request.user,company_id=request.session['company']).filter(proje_id__isnull=True)

    if actigimGorevler:   # actigımGorev varsa
        
        actigimGorevler = actigimGorevler.filter(scheduledTask__isnull=True)  # düzenli görevler hariç
        gorevlerim = gorevlerim.filter(scheduledTask__isnull=True)  # düzenli görevler hariç
        
        filtreliGorevlerim = gorevlerim.union(actigimGorevler)
    else:
        filtreliGorevlerim = gorevlerim.filter(scheduledTask__isnull=True)  # düzenli görevler hariç

    # tüm görev sayısını kontrol ediyoruz
    benimActigimTumGorevler = Gorevler.objects.filter(open_user=request.user,company_id=request.session['company']).filter(proje_id__isnull=True)
    banaAcilanTumGorevler = Gorevler.objects.filter(responsible_user=request.user,company_id=request.session['company']).filter(proje_id__isnull=True)
    tumGorevlerim = benimActigimTumGorevler.union(banaAcilanTumGorevler)
    
    if tumGorevlerim.count() > 1:       # eğer 1 den fazla görev varsa ilk görev kontrolü yapılır
        ilkGorev = False
    else:
        ilkGorev = True

    paginator = Paginator(filtreliGorevlerim, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return  render(request,'gorevListele.html',{'page_obj':page_obj,'ap':ap,'ilkGorev':ilkGorev,'gorevStatus':gorevStatus,'duzenliGorevler':duzenliGorevler}) 

    

@login_required(login_url='/user/login/')
@permission_required('gorevler.change_gorevler',login_url='/user/yetkiYok/')
def gorevGuncelle(request,id):
    gorevform = get_object_or_404(Gorevler,id=id)
    form = GorevForm(request.session['company'],request.POST or None, request.FILES or None,instance=gorevform)
    if form.is_valid() :
        gorev = form.save(commit= False)
        gorev.save()
        messages.success(request,"Görev güncellendi")
        Logla(request,f"Görev güncellendi gorev_id:{gorev.id}")
        return redirect("/gorevler/gorevListele/aktif")

    return  render(request,'gorevGuncelle.html',{'form':form})


def gorevStatuUpdate(request,gorev_id,statu_id,secret):
    gorev = get_object_or_404(Gorevler,id=gorev_id,secret=secret)
    gorev.statu_id = statu_id
    gorev.save()

    if statu_id == 5:
        send_sms(request,gorev.open_user.employee.telephone,f"Görev id:{gorev_id} iptal edildi")

    messages.success(request,"Görev statüsü güncellendi")
    Logla(request,f"Görev statüsü güncellendi gorev_id:{gorev.id} statu:{gorev.statu}")

    return redirect(request.META['HTTP_REFERER'])



@login_required(login_url='/user/login')
@permission_required('gorevler.delete_gorevler',login_url='/user/yetkiYok/')
def gorevSil(request,id):
    gorev = get_object_or_404(Gorevler,id=id)
    gorev.delete()
    messages.success(request,"gorev silindi")
    Logla(request,f"Gorev Silindi gorev_id:{gorev.id}")
    return redirect("/gorevler/gorevListele/aktif")


@login_required(login_url='/user/login')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def gorevGoster(request,id):
    try:
        gorev = Gorevler.objects.get(id=id,company_id=request.session['company'])
    except:
        messages.success(request,"Görev bulunamadı")
        return redirect("/gorevler/gorevListele/aktif")
    form = GorevTamamla(request.POST or None,request.FILES or None, instance=gorev)
    gorevNotuForm = GorevNotuForm(request.POST or None, request.FILES or None)
    gorevNotlar = GorevNotu.objects.filter( gorev_id = id , company_id=request.session['company'] )
    gorevOrderProductForm = GorevOrderProductsForm(request.session['company'],request.POST or None, request.FILES or None)

    print("gorev:" , gorev)

    # bir sayfada birden fazla form olduğu için hangisini çalıştıracağımızı hidden bilgisi ile alıyoruz
    gorevNotEkle = request.POST.get("gorevNotEkle")
    gorevGuncelle = request.POST.get("gorevGuncelle")
    gorevAddProduct = request.POST.get("gorevAddProduct")
    toplamTutar = 0

    #bu göre için order var mı kontrol edilir varsa yazılmış ürünler alınır.
    if gorev.order :    
        orderProducts = OrderProducts.objects.filter(order= gorev.order)
        toplamTutar = sum(orderProducts.values_list('toplam_tutar', flat=True))
    else:
        orderProducts = None

    # Gorev notu ekleme formunu çalıştırmak için
    if gorevNotuForm.is_valid() and gorevNotEkle == "1" :

        gorevNot = gorevNotuForm.save(commit=False)
        gorevNot.company_id = request.session["company"]
        gorevNot.created_date = datetime.datetime.now()
        gorevNot.gorev_id = id
        gorevNot.open_user = request.user
        gorevNot.save()
        messages.success(request,"Göreve not eklendi")
        Logla(request,f"görev id: {id} {gorevNot.description} notu eklendi:{gorev.id}")
        return redirect("/gorevler/gorevGoster/"+str(id) )

        #TODO ekleme sonrası ilgililere mail yada sms gonderimi düşünülebilir


    # Görev güncelleme formu
    if form.is_valid() and gorevGuncelle == "1" :
        print("gorev güncellenecek")
        gorev = form.save(commit= False)
        gorev.company_id=request.session['company']

        gorev.closed_date = datetime.datetime.now()
        gorev.statu_id = 4
        gorev.save()
        
        messages.success(request,"Görev tamamlandı")
        Logla(request,f"Görev:{gorev.id} \"{gorev.title}\"  tamamlandı")
        send_sms(request,gorev.open_user.employee.telephone,f"Görev:{gorev.id} \"{gorev.title}\"  tamamlandı")

        return redirect("/gorevler/gorevListele/aktif")

    # Göreve order ve ürün eklemek için burası çalışır.
    #TODO: stok kontrolü olması ve olmaması durumu için ayrı kontroller ekleyelim
    print("gorevAddProduct:",gorevAddProduct)
    if gorevOrderProductForm.is_valid() and gorevAddProduct == "1":
        print("urun eklenecek")
        #if gorev.problem.customer:
        if gorev.problem:
            print("müşteri problem kaydında tanımlı")
            if gorev.order :
                
                print("order tanımlanmış ürün ekleniyor")
                orderProduct = gorevOrderProductForm.save(commit=False)
                orderProduct.order = gorev.order
                orderProduct.birim_fiyat = orderProduct.product.birim_fiyat
                orderProduct.toplam_tutar = orderProduct.product.birim_fiyat  * orderProduct.amount
                orderProduct.save()
                print(f"{orderProduct.id} numaralı orderPruduct kaydı oluşturuldu")
                Logla(request,f"{orderProduct.id} numaralı orderPruduct kaydı oluşturuldu")

            else:   # order tanımlanmamışsa bir kere tanımlanır ve ürünler orderProdutcs tablosuna eklenir
                print("gorevde order kaydı yok ilk kez tanımlanacak")
                #TODO: şube su an default atanıyor bunu müşteri lokasyonuna göre seçebilmeliyiz
                order = Order(customer = gorev.problem.customer ,statu_id= 23,sube_id=1,company_id=request.session['company'],create_date=datetime.datetime.now())
                order.save()

                gorev.order = order
                gorev.save()

                print(f"{order.id} numaralı order kayıdı oluşturuldu")
                Logla(request,f"{order.id} numaralı order kayıdı oluşturuldu")

                orderProduct = gorevOrderProductForm.save(commit=False)
                orderProduct.order = order
                orderProduct.birim_fiyat = orderProduct.product.birim_fiyat
                orderProduct.toplam_tutar = orderProduct.product.birim_fiyat  * orderProduct.amount
                orderProduct.save()
                Logla(request,f"{orderProduct.id} numaralı orderPruduct kaydı oluşturuldu")
                print(f"{orderProduct.id} numaralı orderPruduct kaydı oluşturuldu")

        else:
            print("problem kaydına müşteri bağlanmalı")
            messages.error(request,"problem kaydına müşteri bağlanmalı")

    # ilk sayfa açılırken çalışır
    gorevStatus = GorevlerStatu.objects.filter(company_id=request.session['company']).exclude(id__in=[1,2,3,4,5])

    if gorev:
        ilkGorev = ilkGorevKontrol(gorev.open_user)
        print("ilkGorev:",ilkGorev)
        return render(request,"gorevGoster.html",{"gorev":gorev,'form':form,
                                                  'gorevNotuForm':gorevNotuForm, 
                                                  'gorevNotlar':gorevNotlar,
                                                  'gorevOrderProductForm':gorevOrderProductForm, 
                                                  'orderProducts':orderProducts,
                                                  'ilkGorev':ilkGorev,
                                                  'statuList':gorevStatus,
                                                  'toplamTutar':toplamTutar})
    else:
        messages("Gorev bulunamadı")
        Logla(request, f"{id}Gorev bulunamadı")
        return redirect("/gorevler/gorevListesi")


def ilkGorevKontrol(user):
    ilkGorev = True
    gorevler = Gorevler.objects.filter(open_user=user)
    if gorevler.count() == 1:
        ilkGorev = True
    else:
        ilkGorev = False
        
    return ilkGorev

def taskViewWithSecret(request,gorev_id,secret):
    

    gorevNotEkle = request.POST.get("gorevNotEkle")
    gorevGuncelle = request.POST.get("gorevGuncelle")
    gorevAddProduct = request.POST.get("gorevAddProduct")

    # gecen oran tanımlanmaz ise if içinde oluşmaması durumunda hata verir.default olarak 0 tanımlanır
    gecenOran = 0          

    try: 
        gorev = Gorevler.objects.get(id=gorev_id,secret=secret)
        form = GorevTamamla(request.POST or None,request.FILES or None, instance=gorev)
    except:
        messages.warning(request,"Görev girişinde secret key hatası")
        Logla(request, f"{gorev_id} {secret} uyumsuz key")
        return redirect("/user/login")

    ilkGorev = ilkGorevKontrol(gorev.open_user)

    # TODO: deadline geçişinde 1 günlük buffer tanımladık bunu ayarlar kısmına alalım
    if gorev.secret_expiredate + datetime.timedelta(days=1)  > datetime.datetime.now():
        print(gorev.deadline)
        if gorev.deadline:  # deadline tanımlı ise gecen gün oransal hesaplanır ve sayfada gösterilir
            
            if datetime.datetime.now() > gorev.deadline:    # 100% den buyuk olamaz
                gecenOran = 100
            else:
                toplamGun = gorev.deadline - gorev.created_date
                toplamGun = toplamGun.days
                kalanGun = gorev.deadline - datetime.datetime.now()
                kalanGun = kalanGun.days
                if toplamGun == 0:      
                    gecenOran = 0
                else:
                    gecenOran = ((toplamGun - kalanGun) / toplamGun) * 100
                    gecenOran = round(gecenOran,0)



        gorevNotuForm = GorevNotuForm(request.POST or None, request.FILES or None)

        #TODO: güvenlik açısından bu kısmı tekrar değerledirelim
        gorevNotlar = GorevNotu.objects.filter( gorev_id = gorev_id )           # !!!!! company kontolu yapılmıyor. key bilgisi ile gelindiği için session da company ve user bilgileri bulunmuyor

        if gorevNotuForm.is_valid() and gorevNotEkle == "1" :   # görev notu ekleme formu
            print("gorev notu eklenecek")
            gorevNot = gorevNotuForm.save(commit=False)
            gorevNot.company_id = gorev.company_id
            gorevNot.created_date = datetime.datetime.now()
            gorevNot.gorev_id = gorev.id
            gorevNot.open_user = gorev.responsible_user

            gorevNot.save()
            messages.success(request,"Göreve not eklendi")
            Logla(request,f"görev id: {id} {gorevNot.description} notu eklendi:{gorev.id}")

        # Görev güncelleme formu
        if form.is_valid() and gorevGuncelle == "1" :   # görev güncelleme formu tamamlanma durumunda çalışır
            gorev = form.save(commit= False)

            gorev.statu_id = 4
            gorev.closed_date = datetime.datetime.now()
            gorev.save()
            #TODO statu tamamlandı ise db de gerekli güncellemeleri yapalım
            #TODO tamamlandı statusunda cozum kısmı acıklama altında goruntulenebilsin

            messages.success(request,"Görev tamamlandı")
            Logla(request,f"user:{gorev.responsible_user} Görev:{gorev.id} \"{gorev.title}\"  tamamlandı")
            send_sms(request,gorev.open_user.employee.telephone,f"Görev:{gorev.id} \"{gorev.title[:20]}\"  tamamlandı")

            sms_content = f"user:{gorev.responsible_user} Görev:{gorev.id} \"{gorev.title[:20]}\"  tamamlandı"
            if getSettings("toyu_adm_taskReg_bilgi",1):
                    send_sms(request,"5326179630",sms_content)
                    send_sms(request,"5322664250",sms_content)


            login(request,gorev.responsible_user)
            Logla(request,f"user:{gorev.responsible_user} User otomatik login oldu ")
            # ilk gorev tamamlandıktan sonra şifre değişikliği yapılır
            if ilkGorev:
                return redirect(f"/user/userChangePassword/{gorev.responsible_user.id}")


        return render(request,"gorevGosterKey.html",{"gorev":gorev,
                                                     'gorevNotuForm':gorevNotuForm, 
                                                     'gorevNotlar':gorevNotlar,
                                                     'form':form,
                                                     'gecenOran':gecenOran,
                                                     'ilkGorev':ilkGorev})

    else: # keyin süresi geçmiş login ekranına yönlendirilir

        return redirect("/user/login")
    
############################################################################
#######################  RAPOR           #################################
############################################################################
#satis = OrderProducts.objects.filter(company_id=request.session['company'],product__urun_grubu=urun).filter(order__create_datestart_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(order__sube=sube).aggregate(Sum('toplam_tutar'))['toplam_tutar__sum']
#iskonto = Order.objects.filter(sube=sube,company_id=request.session['company']).filter(create_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(create_date__month=ay+1).aggregate(Sum('iskonto_tutar'))['iskonto_tutar__sum']
#satis = OrderProducts.objects.filter(order__sube=sube,company_id=request.session['company']).filter(order__create_datestart_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(order__create_date__month=ay+1).aggregate(Sum('toplam_tutar'))['toplam_tutar__sum']
#satis = OrderProducts.objects.filter(order__sube=sube,company_id=request.session['company']).filter(order__create_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(order__create_date__month=ay+1).aggregate(Sum('toplam_tutar'))['toplam_tutar__sum']
#satis = OrderProducts.objects.filter(order__sube=sube,company_id=request.session['company']).filter(order__create_date__gt=datetime.date.today() - datetime.timedelta(days=365)).aggregate(Sum('toplam_tutar'))['toplam_tutar__sum']
#iskonto = Order.objects.filter(sube=sube).filter(company_id=request.session['company'],create_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(create_date__month=ay+1).aggregate(Sum('iskonto_tutar'))['iskonto_tutar__sum']
#satis = OrderProducts.objects.filter(company_id=request.session['company'],order__sube=sube).filter(order__create_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(order__create_date__month=ay+1).aggregate(Sum('toplam_tutar'))['toplam_tutar__sum']

"""@login_required(login_url='/user/login')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def acilan_gorev(request):
    labels=[]
    acilanGorev=[]
    kapatilanGorev=[]
    zamanindaBitenGorev=[]
    zamanindaBitenGorevOrani=[]

    for ay in range(0,datetime.datetime.now().month ):

        labels.append( aylar[ay] )
        acilan_gorev_sayisi = Gorevler.objects.filter(company_id=request.session['company'],created_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(created_date__month=ay+1).count()
        kapatilan_gorev_sayisi = Gorevler.objects.filter(company_id=request.session['company'],closed_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(closed_date__month=ay+1).count()
        
        zamaninda_biten = Gorevler.objects.filter(company_id=request.session['company'],closed_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(closed_date__month=ay+1).filter(closed_date__lt=F('deadline')).count()
        
        acilanGorev.append(acilan_gorev_sayisi)
        kapatilanGorev.append(kapatilan_gorev_sayisi)
        zamanindaBitenGorev.append(zamaninda_biten)
        if kapatilan_gorev_sayisi==0:
            zamanindaBitenGorevOrani.append(0)
        else:
            zamanindaBitenGorevOrani.append(zamaninda_biten/kapatilan_gorev_sayisi)


        
    userList,acikTask,kapatilanGorevSayisi = userTaskCount()
    print("userList:",userList)
    print("acikTask:",acikTask)
    print("kapatilanGorevSayisi:",kapatilanGorevSayisi)

    return JsonResponse(data={  'labels':labels,
                                'data':[
                                        {'label':'Açılan Görev','backgroundColor':'red','data':acilanGorev},
                                        {'label':'Kapatılan Görev','backgroundColor':'green','data':kapatilanGorev}
                                        
                                    ],
                                'data_zamaninda':[
                                        {'label':'Zamanında Biten','backgroundColor':'red','data':zamanindaBitenGorevOrani}
                                       
                                        
                                    ],
                                'userList':userList,
                                'acikTask':acikTask,
                                'kapatilanGorevSayisi':kapatilanGorevSayisi
                              }
                        )"""

@login_required(login_url='/user/login')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def duzenliGorevRapor(request,year,month,type):
    """
        ('1', 'Günlük'),
        ('2', 'Haftalık'),
        ('3', 'Aylık'),
        ('4', 'Yıllık'),
        ('5', 'Saatlik'),
    """
    
    # gunluk tanımlanmış kontrol listesi alınır
    if type == "1":
        gunluk_kontrol_listesi = DuzenliGorevTanim.objects.filter(company_id=request.session['company'],repeat_type=1)
        
    elif type == "2":
        gunluk_kontrol_listesi = DuzenliGorevTanim.objects.filter(company_id=request.session['company'],repeat_type=2)
    elif type == "3":
        gunluk_kontrol_listesi = DuzenliGorevTanim.objects.filter(company_id=request.session['company'],repeat_type=3)
    elif type == "4":
        gunluk_kontrol_listesi = DuzenliGorevTanim.objects.filter(company_id=request.session['company'],repeat_type=4)
    else:
        gunluk_kontrol_listesi = DuzenliGorevTanim.objects.filter(company_id=request.session['company'])
    #bulunduğumuz ayda kaç gün var. tablodaki stunları ve değerleri buna göre kontrol ediyoruz
    bugun = datetime.date.today()
    ay_gun_sayisi = calendar.monthrange(year, month)[1]
    gunler = [i for i in range(1,ay_gun_sayisi+1)]
    
    current_year_month = str(year) + "_" + str(month)
    last_month = month - 1 if month > 1 else 12
    last_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    
    #print("ay_gun_sayisi:",ay_gun_sayisi)
    data = []
    labels_data = []
    
    # her bir kontrol maddesi için tüm aylık günlerde kontrol yapılır
    for gunluk_kontrol in gunluk_kontrol_listesi:
        
        satir = []
        label_value = []

        satir.append(gunluk_kontrol.title[:10])

        
        for day in range (1,ay_gun_sayisi+1):
            
            gun = datetime.date(year, month, day)  # ayın ilgili gunu belirlenir ve kontrol yapılır
            
            gun_baslangic = datetime.datetime.combine(gun+ timedelta(days=-1), datetime.datetime.max.time())  # 2024-12-21 00:00:00
            gun_bitis = datetime.datetime.combine(gun + timedelta(days=1), datetime.datetime.min.time())  # 2024-12-23 00:00:00

            gunluk_gorev = Gorevler.objects.filter( company_id=request.session['company'],deadline__range=(gun_baslangic, gun_bitis),scheduledTask_id=gunluk_kontrol.id)
            
            """
            value 
            0: görev tanımlanmamış 
            1:zamanında tamamlanmış 
            2:geçikmiş 
            3:tamamlanmamış 
            4:bekliyor
            5:birden fazla görev tanımlanmış
            """
            
            gunluk_gorev_list = list(gunluk_gorev)
            if len(gunluk_gorev_list) > 1:      # birden fazla görev tanımlanmışsa
                value = 5
            elif gunluk_gorev_list:
                gorev = gunluk_gorev_list[0]
                #print("gorev:",gorev)
                
                if gorev.closed_date:
                    #print("closed_date:",gunluk_gorev[0].closed_date)
                    #print("deadline:",gunluk_gorev[0].deadline)
                    
                    value = 1 if gorev.closed_date <= gorev.deadline else 2
                    # zamanında tamamlanmmımşsa 1, geçikmişse 2
                else:
                    if gorev.deadline < datetime.datetime.now():
                        value = 3 # gorev tamamlanmamışsa
                      
                    else:  
                        value = 4 # bekliyor
                        print("day:",day," gorev 4 :",gorev)
            else:
                value = 0
                
            satir.append(value)
            label_value.append(value)
            
        sorumlu = gunluk_kontrol.responsible_user if gunluk_kontrol.responsible_user else gunluk_kontrol.department if gunluk_kontrol.department else "Tanımsız"
        
        data.append(satir)    
        labels_data.append({'label': gunluk_kontrol.title, 'sorumlu':sorumlu,'data': label_value})

    return render(request,"duzenliGorevRapor.html",{
        'json_data': labels_data,'data':data,'gunler':gunler,'gunluk_kontrol_listesi_count':gunluk_kontrol_listesi.count(),
        'last_month':last_month,'last_year':last_year,'next_month':next_month,'next_year':next_year,'current_year_month':current_year_month ,
        "year":year,"month":month,"type":type})

                        
def userTaskCount(request):

    responsible_users = Gorevler.objects.all().filter(company_id=request.session['company']).values_list('responsible_user', flat=True).distinct()
    userList = list(responsible_users)

    userNameList=[]
    acikTask = []
    kapatilanGorevSayisi = []
    toplamTaskList = []

    for user in userList:
        
        toplamTaskSayisi = Gorevler.objects.filter(responsible_user=user).count()
        kapatilmisTaskSayisi = Gorevler.objects.filter(responsible_user=user).filter(closed_date__isnull=False).count()
        acikTaskSayisi = toplamTaskSayisi - kapatilmisTaskSayisi

        acikTask.append(acikTaskSayisi)
        toplamTaskList.append(toplamTaskSayisi)
        kapatilanGorevSayisi.append(kapatilmisTaskSayisi)
        try:

            user = User.objects.get(id=user)
            userNameList.append(f"{user.first_name} {user.last_name}")
        except:
            userNameList.append("Tanımsız")
    
    userList = userNameList # query set olan user listesi string listeye dönüştürülür

    return userList,acikTask,kapatilanGorevSayisi,toplamTaskList


def taskStatuOran(request):
    statuList = GorevlerStatu.objects.all()
    statuOran = []
    for statu in statuList:
        #statuAdet =Gorevler.objects.filter(company_id=request.session['company'],statu=statu).count()
        statuAdet =Gorevler.objects.filter(statu=statu).count()
        statuOran.append({'x':statu.statu,'y':statuAdet})

    return statuOran          

@login_required(login_url='/user/login')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def rapor_gorev(request):

    labels=[]
    acilanGorev=[]
    kapatilanGorev=[]
    zamanindaBitenGorev=[]
    zamanindaBitenGorevOrani=[]

    for ay in range(0,datetime.datetime.now().month ):

        labels.append( aylar[ay] )
        acilan_gorev_sayisi = Gorevler.objects.filter(company_id=request.session['company'],created_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(created_date__month=ay+1).count()
        kapatilan_gorev_sayisi = Gorevler.objects.filter(company_id=request.session['company'],closed_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(closed_date__month=ay+1).count()
        
        zamaninda_biten = Gorevler.objects.filter(company_id=request.session['company'],closed_date__gt=datetime.date.today() - datetime.timedelta(days=365)).filter(closed_date__month=ay+1).filter(closed_date__lt=F('deadline')).count()
        
        acilanGorev.append(acilan_gorev_sayisi)
        kapatilanGorev.append(kapatilan_gorev_sayisi)
        zamanindaBitenGorev.append(zamaninda_biten)
        if kapatilan_gorev_sayisi==0:
            zamanindaBitenGorevOrani.append(0)
        else:
            oran = round((zamaninda_biten/kapatilan_gorev_sayisi) * 100 , 0)
            zamanindaBitenGorevOrani.append(oran )

        acilanGorevAylik = {"labels":labels,"data":acilanGorev}
        kapatilanGorevAylik = {"labels":labels,"data":kapatilanGorev}
        zamanindaBitenGorevOraniAylik = {"labels":labels,"data":zamanindaBitenGorevOrani}

    userList,acikTask,kapatilanGorevSayisi,toplamTaskList = userTaskCount(request)
    taskStatuOranData = taskStatuOran(request)
  

    return render(request,"rapor_gorev.html",{ 'acilanGorevAylik':acilanGorevAylik,
                                                'kapatilanGorevAylik':kapatilanGorevAylik,
                                                'zamanindaBitenGorevOraniAylik':zamanindaBitenGorevOraniAylik,
                                                'userList':userList,
                                                'acikTask':acikTask,
                                                'kapatilanGorevSayisi':kapatilanGorevSayisi,
                                                'taskStatuOranData':taskStatuOranData,
                                                'toplamTaskList':toplamTaskList

                                              })

@login_required(login_url='/user/login/')
def takvim_task(request):
    
    
    return  render(request,'takvim_task.html',{} )


@login_required(login_url='/user/login')
def gorev_takvim_data(request):
    events_arr =[]
    lastmonth =datetime.date.today() + datetime.timedelta(days=-61)
    company = Company.objects.get(id= request.session['company'])
    print("company:",company)

    if request.user == company.user:    # Firmanın admini ise firmanın tüm görevlerini görebilir
        print("admin takvimi gorecek")
        gorevler = Gorevler.objects.filter(deadline__gt = lastmonth,company_id=request.session['company'])
    else:
        #admin değilse sadece kendisine açılan ve kendisinin açtığı görevleri görebilir
        #gorevler = Gorevler.objects.filter(responsible_user__or=request.user,open_user__or=request.user).filter(deadline__gt = lastmonth,company_id=request.session['company'])
        gorevler = Gorevler.objects.filter( 
                Q(responsible_user=request.user) | Q(open_user=request.user),
                deadline__gt=lastmonth,
                company_id=request.session['company']
            )

    for gorev in gorevler:
        print("gorev",gorev)
        if gorev.start_date:
            start_date = datetime.datetime.strftime(gorev.start_date, '%Y-%m-%d %H:%M')
        else:
            if gorev.deadline:
                start_date = datetime.datetime.strftime(gorev.deadline, '%Y-%m-%d 00:00')
            else:
                start_date = ""

        if gorev.deadline:
            end_date = datetime.datetime.strftime(gorev.deadline, '%Y-%m-%d %H:%M')
        else:
            end_date = ""

        color = 'white'
        textColor= 'white'
        title =""
        description = ""

        if gorev.statu.id == 4:    #tamamlandı
            if gorev.closed_date :
                if gorev.closed_date <= gorev.deadline: # zamanında kapatılmış mı kontrol edilir.   
                    color = '#30E3DF'   #green
                else:
                    color = '#D61355'   #red
        elif gorev.statu.id == 5:      #iptal
            color = '#808080'       #gri renk
        else:                       #açıldı çalışılıyor beklemede statulerinde mavi
            color = '#0F6292'       #mavi

        if gorev.responsible_user:
            first_name =  gorev.responsible_user.first_name
            last_name = gorev.responsible_user.last_name
        
        title = gorev.title
        description = gorev.description
        if description:
            description = description[:20]
            
        events_arr.append( {'id':gorev.id,'title': "Durum:"+gorev.statu.statu +" " +first_name+" " +last_name + " " + title, 'start': start_date,'end': end_date,'description':description  , 'color': color ,'textColor':textColor})


    #y = json.dumps(events_arr ,sort_keys=True,  indent=1,  default=default)    # array i json formatına donusturduk
    serialized= json.dumps(events_arr, sort_keys=False, indent=3,ensure_ascii=False)   # array i json formatına donusturduk
    return HttpResponse(serialized)




############################################################################
#######################  GÖREV statu      #################################
@login_required(login_url='/user/login/')
@permission_required('gorevler.add_gorevler',login_url='/user/yetkiYok/')
def gorevStatuAdd(request):
  
    form = GorevStatuForm(request.POST or None,request.FILES or None)

    if form.is_valid():
        gorevStatu = form.save(commit=False)
        gorevStatu.company_id    = request.session['company']
        gorevStatu.save()

        messages.info(request," görev Statusu tanımlandı")
        Logla(request,f"Görev Statu eklendi gorevstatu_id:{gorevStatu.id}")
        return redirect("/gorevler/gorevStatuList")


    return  render(request,'gorevStatuAdd.html',{'form':form}) 

@login_required(login_url='/user/login/')
@permission_required('gorevler.view_gorevler',login_url='/user/yetkiYok/')
def gorevStatuList(request,ap="all"):

    gorevStatus = GorevlerStatu.objects.filter(company_id=request.session['company'])

    return  render(request,'gorevStatuListele.html',{'gorevStatus':gorevStatus}) 

@login_required(login_url='/user/login/')
@permission_required('gorevler.change_gorevler',login_url='/user/yetkiYok/')
def gorevStatuCustomUpdate(request,id):
    gorevStatu = get_object_or_404(GorevlerStatu,id=id,company_id=request.session['company'])
    print("gorevStatu:",gorevStatu)
    form = GorevStatuForm(request.POST or None, request.FILES or None,instance=gorevStatu)

    if form.is_valid() :
        gorevStatu = form.save(commit= False)
        gorevStatu.save()
        messages.success(request,"Görev Statu tablosu güncellendi")
        Logla(request,f"Görev Statu tablosu güncellendi gorev_id:{gorevStatu.id}")
        return redirect("/gorevler/gorevStatuList")

    return  render(request,'gorevStatuGuncelle.html',{'form':form})


@login_required(login_url='/user/login')
@permission_required('gorevler.delete_gorevler',login_url='/user/yetkiYok/')
def gorevStatuDelete(request,id):
    gorevStatu = get_object_or_404(GorevlerStatu,id=id)
    gorevStatu.delete()
    messages.success(request,"Görev statüsü silindi")
    Logla(request,f"Gorev Statu Silindi gorevStatu_id:{gorevStatu.id}")
    return redirect("/gorevler/gorevStatuList")