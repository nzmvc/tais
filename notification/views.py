from django.shortcuts import render
from gorevler.models import Gorevler
from notification.forms import NotificationForm
from notification.models import Notification,ReadFlag
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, response
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.contrib import messages
from user.views import Logla, LoglaSms
from user.models import SmsProblem, User
import datetime
import os
from twilio.rest import Client
from decouple import config
import requests
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from twilio.twiml.messaging_response import MessagingResponse 

import json  # JSON verilerini işlemek için
def whatsappMessage(request,phone,msg):

    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_AUTH_TOKEN')
    twilioclient = Client(account_sid, auth_token)
    print("cliennt:" , twilioclient)
        
    message = twilioclient.messages.create(
        from_='whatsapp:+16073182890',
        to='whatsapp:+90' + phone.replace(" ", "")[-10:],
        content_sid="HX2d0a9ca9808cede0cd16c1c90d4388fc",   # tek seferlik mesaj idsi
        content_variables=json.dumps({"1": msg}),
        )

    return HttpResponse(f"WhatsApp mesajı gönderildi. SID: {message.sid}")

def whatsappTaskMessage(request,phone,task):

    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_AUTH_TOKEN')
    twilioclient = Client(account_sid, auth_token)
    print("cliennt:" , twilioclient)
        
    message = twilioclient.messages.create(
        from_='whatsapp:+16073182890',
        to='whatsapp:+90' + phone.replace(" ", "")[-10:],
        content_sid="HX2d0a9ca9808cede0cd16c1c90d4388fc",
        content_variables=json.dumps({"1": task.title}),
        body=task.title,
        persistent_action=[
            {
                "type": "url",
                "text": "Tamamlandı",
                "url": f"https://your-domain.com/update-task-status?task_id={task.id}&status=completed"
            },
            {
                "type": "url",
                "text": "Tamamlanmadı",
                "url": f"https://your-domain.com/update-task-status?task_id={task.id}&status=not_completed"
            }
        ]
        )

    print(message.sid)
    return HttpResponse(f"WhatsApp mesajı gönderildi. SID: {message.sid}")






@csrf_exempt
def whatsappWebHook(request):
    #https://www.twilio.com/docs/messaging/guides/webhook-request
    
    user = request.POST.get('From')
    body = request.POST.get('Body')
    date_created = request.POST.get('date_created')
    to_number = request.POST.get("To")  # Mesajın gönderildiği numara
    
    ButtonPayload = request.POST.get("ButtonPayload")  # Görev ID'si butondan alınıyor
    task_id = ButtonPayload
    
    print(f'{user} sent {body} to {to_number} task_id:{task_id} date_created:{date_created}')
    logger = logging.getLogger(__name__)    

    if request.method != "POST":
        print("Geçersiz HTTP yöntemi kullanıldı.")
        logger.warning("Geçersiz HTTP yöntemi kullanıldı.")
        return JsonResponse({"error": "Sadece POST isteklerine izin verilir."}, status=405)

    # Görev durumu güncelleme işlemi
    if body == "Tamamlandı":
        print("Tamamlandı çalıştı")
        if not task_id:
            print("Eksik görev ID'si.")
            logger.error("Eksik görev ID'si.")
            return JsonResponse({"error": "Eksik görev ID'si."}, status=400)
        
        task = get_object_or_404(Gorevler, id=task_id)
        print(f"Görev {task} 'Tamamlandı' olarak güncellenecek .statu {task.statu_id}")
        print(f"company_id: {task.company_id}")
        task.statu_id = 4
        task.closed_date = datetime.datetime.now()
        task.save()
        print(f"Görev {task} 'Tamamlandı' olarak güncellendi.statu {task.statu_id}")
        logger.info(f"Görev {task_id} 'Tamamlandı' olarak güncellendi.")
        return JsonResponse({"message": "Görev durumu tamamlandı olarak güncellendi."}, status=200)

    elif body == "Tamamlanmadı":
        print("Tamamlanmadı çalıştı")
        if not task_id:
            print("Eksik görev ID'si.")
            logger.error("Eksik görev ID'si.")
            return JsonResponse({"error": "Eksik görev ID'si."}, status=400)

        task = get_object_or_404(Gorevler, id=task_id)
        print(f"Görev {task} 'Tamamlanmadı' olarak güncellenecek .statu {task.statu_id}")
        task.statu_id = 3
        task.save()
        logger.info(f"Görev {task_id} 'Tamamlanmadı' olarak güncellendi.")
        print(f"Görev {task} 'Tamamlanmadı' olarak güncellendi.statu {task.statu_id}")
        return JsonResponse({"message": "Görev durumu tamamlanmadı olarak güncellendi."}, status=200)

    else:
        logger.warning(f"Geçersiz yanıt: {body}")
        print(f"Geçersiz yanıt: {body}")
        return JsonResponse({"error": "Geçersiz yanıt."}, status=400)


    
@login_required(login_url='/user/login/')
def notificationAdd(request):

    form = NotificationForm(request.session['company'],request.POST or None,request.FILES or None)
    
    if form.is_valid() :
        notification = form.save()
        notification.company_id = request.session['company']
        notification.save()

        recepients = request.POST.getlist('recepients')
        for r in recepients:
            user= User.objects.get(id=r)
            read = ReadFlag(message = notification,recipient =user)
            read.save()
        messages.info(request," notification tanımlandı")
        Logla(request,f'notification eklendi notificationID:{notification.pk}')
        return redirect("/notification/notificationList")
    return  render(request,'notificationAdd.html',{'form':form}) 


@login_required(login_url='/user/login/')
@permission_required('notification.view_notification',login_url='/user/yetkiYok/')
def notificationList(request):
    keyword = request.GET.get("keyword")
    if keyword:
        notifications = Notification.objects.filter(product_name__contains = keyword).filter(closed_date=None,company_id=request.session['company'])
        return  render(request,'taskList.html',{'notifications':notifications})    

    notifications = Notification.objects.filter(company_id=request.session['company']).order_by('-created_date')

    return  render(request,'notificationList.html',{'notifications':notifications}) 



############################################################################
####################### SEND _SMS_       #################################
############################################################################


#<?xml version='1.0' encoding='utf-8'?>
def send_sms(request,gsm_no,gsm_mesaj):
    sms_donus={ "99":"UNKNOWN_ERROR",
                "00":"SUCCESS",
                "97":"USE_POST_METHOD",
                "91":"MISSING_POST_DATA",
                "89":"WRONG_XML_FORMAT",
                "87":"WRONG_USER_OR_PASSWORD",
                "85":"WRONG_SMS_HEADER",
                "84":"WRONG_SEND_DATE_TIME",
                "83":"EMPTY_SMS",
                "81":"NOT_ENOUGH_CREDITS",
                "77":"DUPLICATED_MESSAGE",
                }
    
    #gsm_mesaj = sms_icerik_duzekt(gsm_mesaj)

    sms_data ="<sms>"
    sms_data +="<username>nazimavci</username>"
    sms_data +="<password>5567406b75a19855187347c04549be2c</password>"
    sms_data +="    <header>TEKNOLIKYA</header>"
    
    """sms_data +="<username>gursuyapi</username>"
    sms_data +="<password>1f6d3e8e0cfda061f2a7f0dda92fb69b</password>"
    sms_data +="    <header>GURSUYAPI</header>"""
    sms_data +="    <validity>2880</validity>"
    sms_data +="    <message>"
    sms_data +="        <gsm>"
    sms_data +="            <no>90"+gsm_no.replace(" ","")[-10:]+"</no>"
    sms_data +="        </gsm>"
    sms_data +="        <msg>"+gsm_mesaj+"</msg>"
    sms_data +="    </message>"
    sms_data +="</sms>"

    #headers = {'Content-Type': 'application/xml'} # set what your server accepts
    headers = {'Content-Type': 'application/xml; charset=UTF-8',"Content-Encoding": "UTF-8"} # turkçe karakter gönderebilmek için
    
    SEND_SMS_URL = "http://panel.1sms.com.tr:8080/api/smspost/v1"

    #messages.info(request,"sms gönderimi yapılacak")
    try:
        req_sms =requests.post(SEND_SMS_URL, data=sms_data.encode('utf-8'),headers=headers)
      

        #messages.info(request,f"SMS :{sms_donus[req_sms.text[:2]]}")
        Logla(request,f"{gsm_no} numarasına sms gonderildi sonu:{sms_donus[req_sms.text[:2]]}")
        LoglaSms(request,f"__{gsm_no}__numarasına sms gonderildi__mesaj:{gsm_mesaj}__sonuç:{sms_donus[req_sms.text[:2]]}")
        
        if req_sms.text[:2] != "00":
            hataKayit = SmsProblem(telephone=gsm_no,message=gsm_mesaj,status=req_sms.text[:2],last_error=sms_donus[req_sms.text[:2]],try_count=1)
            hataKayit.save()
            Logla(request,f"gitmeyen sms kaydedildi id:{hataKayit.id} tel:{gsm_no} mesaj:{gsm_mesaj} sonuç:{sms_donus[req_sms.text[:2]]}")

        return req_sms.text
    except Exception as e:
        messages.error(request,f"SMS gönderiminde hata yaşandı hata:{e}")
        Logla(request,f"{gsm_no} numarasına sms gonderiminde hata yaşandı hata: {e} ")
        LoglaSms(request,f"{gsm_no} numarasına sms gonderiminde hata yaşandı hata: {e} ")
