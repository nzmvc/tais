from django.shortcuts import render
from .forms import DokumanForm
from django.contrib.auth.models import User
from .models import Dosyalar
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, response
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.contrib import messages
from user.views import Logla
from django.utils.crypto import get_random_string
import datetime

# Create your views here.
############################################################################
#######################       Dokuman        #################################
############################################################################
@login_required(login_url='/user/login/')
@permission_required('dokumanlar.view_dosyalar',login_url='/user/yetkiYok/')
def dokumanView(request,id):
    dosya = Dosyalar.objects.get(id=id,company_id = request.session['company'])
    
    return  render(request,'dokumanView.html',{'dosya':dosya})

@login_required(login_url='/user/login/')
@permission_required('dokumanlar.add_dosyalar',login_url='/user/yetkiYok/')
def dokumanAdd(request):
    form = DokumanDetailForm(request.session['company'],request.POST or None,request.FILES or None)
    user = User.objects.get(username=request.user)

    if form.is_valid():
        try:
            dokuman = form.save(commit= False)
            dokuman.created_date = datetime.datetime.now()
            dokuman.created_user = user
            dokuman.company_id = request.session['company']
            dokuman.secret = get_random_string(20)
            dokuman.save()
            #TODO hata kontrolü try except
            messages.info(request,"Dokuman eklendi") 
            
            Logla(request,f"Dokuman eklendi")
            return redirect("/dokumanlar/dokumanList/")
        except Exception as e:
            messages.error(request,"Dokuman eklenemedi. Hata: "+str(e)) 
            Logla(request,f"Dokuman eklenemedi Hata: {str(e)}")

    return  render(request,'dokumanAdd.html',{'form':form})

@login_required(login_url='/user/login/')
@permission_required('dokumanlar.view_dosyalar',login_url='/user/yetkiYok/')
def dokumanList(request):
    
    keyword = request.GET.get("keyword")
    if keyword:
        dokumanlar = Dosyalar.objects.filter( aciklama__contains = keyword,company_id = request.session['company']) 
        return  render(request,'dokumanListele.html',{'dokumanlar':dokumanlar}) 

    dokumanlar = Dosyalar.objects.filter(company_id = request.session['company'])
    return  render(request,'dokumanListele.html',{'dokumanlar':dokumanlar}) 


@login_required(login_url='/user/login/')
@permission_required('dokumanlar.change_dosyalar',login_url='/user/yetkiYok/')
def dokumanUpdate(request,id):
    dokuman = get_object_or_404(Dosyalar,id=id,company_id = request.session['company'])
    form = DokumanForm(request.POST or None, request.FILES or None,instance=dokuman)
    if form.is_valid() :
        dokuman = form.save(commit= False)
        dokuman.save()
        messages.success(request,"döküman güncellendi")
        Logla(request,f"Döküman güncellendi")
        return redirect("/dokumanlar/dokumanList")

    return  render(request,'projeUpdate.html',{'form':form})

@login_required(login_url='/user/login')
@permission_required('dokumanlar.delete_dosyalar',login_url='/user/yetkiYok/')
def dokumanSil(request,id):
        dokuman = get_object_or_404(Dosyalar,id=id,company_id = request.session['company'])
        dokuman.delete()
        messages.success(request,"Döküman silindi")
        Logla(request,"Döküman silindi")
        #return redirect("/dokumanlar/dokumanList")
        return redirect(request.META['HTTP_REFERER'])

