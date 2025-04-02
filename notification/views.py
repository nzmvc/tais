from django.shortcuts import render
from gorevler.models import Gorevler
from notification.forms import NotificationForm
from notification.models import Notification,ReadFlag
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, response
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.contrib import messages
from user.views import Logla
from user.models import User
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

