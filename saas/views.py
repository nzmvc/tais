import random
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,Permission,Group
from django.http import HttpResponse, response
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.contrib import messages
from user.views import Logla, createUsername
from saas.models import Company, CompanyModules, CompanyStatus, Modules
from saas.forms import CompanyForm
import datetime
from django.core.paginator import Paginator
# Create your views here.



@login_required(login_url='/user/login/')
def companyAdd(request):

    form = CompanyForm(request.POST or None, request.FILES or None)
    
    if form.is_valid() :
        yetkili_ad = form.cleaned_data['yetkiliAd']
        yetkili_soyad = form.cleaned_data['yetkiliSoyad']
        yetkili_telefon = form.cleaned_data['yetkiliTelefon']
        yetkili_email = form.cleaned_data['yetkiliEmail']

        company = form.save(commit=False)
        company.open_user = request.user
        company.created_date = datetime.datetime.now()

        username = createUsername(yetkili_email, yetkili_telefon, yetkili_ad, yetkili_soyad)     # kullanıcı adı oluşturulur

        newUser = User( username = username,email=yetkili_email, first_name=yetkili_ad, last_name=yetkili_soyad,is_active=1)

        password = generate_password()
        newUser.set_password(password)      # sistem üzerinde kullanıcının şifresi tanımlanır.
        newUser.save()
        newUser.employee.telephone = yetkili_telefon      # user ile employee tablosu onetoone bağlı
        newUser.employee.company = company
        company.user = newUser
        company.save()
        newUser.employee.save()
        
        messages.info(request,f"Company:{company} tanımlandı.admin  user: {newUser.username} password:{password}")
        Logla(request,f'Firma eklendi ')

        ##############    tüm modulleri tanımlanıyor.
        for m in Modules.objects.all():
            cm = CompanyModules(company=company,modules=m)
            cm.save()
        
        ##############  tüm moduller için grup yetkileri veriliyor.
        grp_list = Group.objects.all()
        for grp in grp_list:
            grp.user_set.add(newUser)
            Logla(request,f'{newUser} için grup tanımlaması yapıldı : {grp.name} ')


        return redirect("/saas/companyList/active")
    
    return  render(request,'companyAdd.html',{'form':form}) 



@login_required(login_url='/user/login/')
#@permission_required('user.urun_listele',login_url='/user/yetkiYok/')
def companyList(request,ap):
    keyword = request.GET.get("keyword")
    if keyword:
        companys = Company.objects.filter(product_name__contains = keyword,company_id=request.session['company']).filter(closed_date=None)
        return  render(request,'companyList.html',{'companys':companys})    

    
    if ap == "all":
        companys = Company.objects.all().order_by('-created_date')
    elif ap == "active":
        companys = Company.objects.filter(active = True).order_by('-created_date')
    elif ap == "pasive":
        companys = Company.objects.filter(active = False).order_by('-created_date')
    elif ap == "yeni":
        companys = Company.objects.filter(active = True).order_by('-created_date')
    elif ap == "eski":
        companys = Company.objects.filter(active = True).order_by('created_date')
        

    # register olan firma listesine loglama yapılıyor.
    if request.method == "POST":

        note = request.POST.get("note")
        company_id = request.POST.get("company_id")
        lead_company = Company.objects.get(id=company_id)
        
        # eğer register olan firma lead tablosunda yoksa oluşturulur
        if not Lead.objects.filter(approved_company_id=company_id).exists():
            new_lead = Lead(
                contact_name = lead_company.telefon if lead_company.telefon is not None else ".",
                company_name = lead_company.name if lead_company.name is not None else ".",
                phone = lead_company.telefon if lead_company.telefon is not None else ".",
                approved_company_id=company_id, 
                company_id=1, 
                user = request.user,
                status_id=1)
            new_lead.save()
            
            # eğer statu tanımlı değilse
            if not CompanyStatus.objects.filter(id=1 ).exists():
                companyStatus = CompanyStatus(name="Lead Tanımlandı",description="Yeni firma kaydı")
                companyStatus.save()
                
            lead_company.status_id = 1
            lead_company.save()
            Logla(request,f"{lead_company.name} şirketi için yeni bir lead oluşturuldu.")
        
        lead = Lead.objects.get(approved_company_id=company_id)
        leadNote = LeadNote()
        leadNote.lead = lead
        leadNote.note = note
        leadNote.user = request.user
        leadNote.company_id = request.session['company']
        leadNote.save()
        Logla(request,f"{lead.company_name} şirketi için {lead.contact_name} kişisi için yeni bir not eklendi.")

        return redirect(request.META['HTTP_REFERER'])
    
    
    paginator = Paginator(companys, 25) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_page = paginator.num_pages

    return  render(request,'companyList.html',{'companys':companys,'page_obj':page_obj}) 

@login_required(login_url='/user/login/')
#@permission_required('user.urun_yonetim',login_url='/user/yetkiYok/')
def companyUpdate(request,id):
    company= get_object_or_404(Company,id=id)
    form = CompanyForm(request.POST or None, request.FILES or None,instance=company)
    if form.is_valid() :
        form.save()
        messages.success(request,"Firma güncellendi")
        Logla(request,f'Firma guncellendi companyId:{id}')
        if company.logo:
            request.session['companyLogoUrl'] = company.logo.url
        
        return redirect("/saas/companyList/aktif")

    return  render(request,'companyUpdate.html',{'form':form})

@login_required(login_url='/user/login')
#@permission_required('user.urun_yonetim',login_url='/user/yetkiYok/')
def companyDelete(request,id):
    company = get_object_or_404(Company,id=id)
    company.delete()
    messages.success(request,"Firma silindi")
    Logla(request,f'Firma silindi companyId:{id}')
    return redirect("/saas/companyList/aktif")

@login_required(login_url='/user/login')
#@permission_required('user.urun_yonetim',login_url='/user/yetkiYok/')
def companyStatu(request,id,statu):
    company = get_object_or_404(Company,id=id)
    if company :
        if statu == "1":
            company.active = 1
            Logla(request,f'Firma statu aktif companyId:{id}')
        else:
            company.active = 0
            Logla(request,f'Firma statu pasif companyId:{id}')
        company.save()

    messages.success(request,"Firma silindi")
    return redirect("/saas/companyList/aktif")

@login_required(login_url='/user/login')
def companyView(request,id):
    company = Company.objects.get(id=request.session['company'])

    if company :
        return render(request,"companyView_v2.html",{"company":company,'form':form})
    else:
        messages.info("Firma bulunamadı bulunamadı")
        return redirect("/gorevler/gorevlistesi/aktif")

@login_required(login_url='/user/login/')
#@permission_required('user.urun_yonetim',login_url='/user/yetkiYok/')
def myCompanyUpdate(request):
    company= get_object_or_404(Company,id=request.session["company"]) 
    form = CompanyForm(request.POST or None, request.FILES or None,instance=company)
    if form.is_valid() :
        form.save()
        messages.success(request,"Firma bilgileri güncellendi")
        Logla(request,f'Firma guncellendi companyId:{id}')
        if company.logo:
            request.session['companyLogoUrl'] = company.logo.url    # company logo url bilgisi session a atılıyor
        return redirect(request.META.get('HTTP_REFERER'))

    return  render(request,'companyUpdate.html',{'form':form})