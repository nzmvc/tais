import datetime
import json
from django.utils.timezone import now
import sys,os,django,requests

from twilio.rest import Client
from decouple import config
from django.utils.timezone import make_naive

# Proje kök dizinini Python yoluna ekleyin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

script_dir = os.path.dirname(os.path.abspath(__file__))

# Proje kök dizinini ekleyin
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

# Django ayarlarını kullanabilmek için ortam değişkenlerini ayarlayın
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyu.settings')
django.setup()

from gorevler.models import Gorevler, GorevlerStatu
def whatsappTaskMessage(phone,task):

    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_AUTH_TOKEN')
    
    twilioclient = Client(account_sid, auth_token)

    print("cliennt:" , twilioclient)
    
    # WhatsApp Card içeriğini bir string değişkenine atayın
    card_content = json.dumps({
        # Yukarıdaki JSON yapısını buraya yapıştırın
    })
    
    message = twilioclient.messages.create(
    from_='whatsapp:+16073182890',
    to='whatsapp:+90' + phone.replace(" ", "")[-10:],
    content_variables=json.dumps({"1": task.title, "2": str(task.id)}),
    #content_sid="HX1b4aca9bd56c7936c9ecb06006f5156c",
    content_sid="HX62dd3cbe8f7313118ef5ce1bde173a4d",

    )
 
  

    print(message.sid)


def LoglaToFile(message):

    filename = "log_task_kontrol.txt"

    with open(filename,"a", encoding="utf-8") as d:
        d.write( f'{datetime.datetime.now()}-message:{message} \r' )

turkce=[("Ç","C"),("Ö","O"),("İ","I"),("Ş","S"),("Ü","U"),("Ğ","G")]
def sms_icerik_duzekt(str):
    str = str.upper()
    for ch in turkce:
        str = str.replace(ch[0],ch[1])
    return str

def send_sms(gsm_no,gsm_mesaj):
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
    sms_data ="<sms>"
    sms_data +="<username>nazimavci</username>"
    sms_data +="<password>5567406b75a19855187347c04549be2c</password>"
    sms_data +="    <header>TEKNOLIKYA</header>"
    #sms_data +="<username>gursuyapi</username>"
    #sms_data +="<password>1f6d3e8e0cfda061f2a7f0dda92fb69b</password>"
    #sms_data +="    <header>GURSUYAPI</header>"
    sms_data +="    <validity>2880</validity>"
    sms_data +="    <message>"
    sms_data +="        <gsm>"
    sms_data +="            <no>90"+gsm_no.replace(" ","")[-10:]+"</no>"
    sms_data +="        </gsm>"
    sms_data +="        <msg>"+gsm_mesaj+"</msg>"
    sms_data +="    </message>"
    sms_data +="</sms>"

    headers = {'Content-Type': 'application/xml'} # set what your server accepts

    SEND_SMS_URL = "http://panel.1sms.com.tr:8080/api/smspost/v1"

    try:
        req_sms =requests.post(SEND_SMS_URL, data=sms_data.encode('utf-8'),headers=headers)
      
        LoglaToFile(f"__{gsm_no}__numarasına sms gonderildi__mesaj:{gsm_mesaj}__sonuç:{sms_donus[req_sms.text[:2]]}")
        
        if req_sms.text[:2] != "00":
            #hataKayit = SmsProblem(telephone=gsm_no,message=gsm_mesaj,status=req_sms.text[:2],last_error=sms_donus[req_sms.text[:2]],try_count=1)
            #hataKayit.save()
            LoglaToFile(f"gitmeyen sms kaydedildi  tel:{gsm_no} mesaj:{gsm_mesaj} sonuç:{sms_donus[req_sms.text[:2]]}")

        return req_sms.text
    except Exception as e:
        
        LoglaToFile(f"{gsm_no} numarasına sms gonderiminde hata yaşandı hata: {e} ")



def close_expired_tasks():
    """
    Deadline'ı geçen ve numberOfDayOpen süresi dolmuş görevleri otomatik kapatır.
    """
    # Görevler için sonlandırma statüsü
    #close_status = GorevlerStatu.objects.filter(is_end=True).first()
    close_status = GorevlerStatu.objects.filter(statu="Otomatik kapantıldı").first()

    if not close_status:
        close_status = GorevlerStatu(statu ="Otomatik kapantıldı", aciklama="Otomatik kapantıldı", is_end=True)
        close_status.save()
        
        print("Sonlandırma statüsü tanımlandı. ")


    # Şu anki tarih ve saat
    current_time = now()

    # Güncellenmesi gereken görevleri filtreleme
    expired_tasks = Gorevler.objects.filter(
        deadline__lt=current_time,  # Deadline geçmiş görevler
        statu__is_end=False,  # Henüz kapatılmamış görevler
        scheduledTask__isnull=False,  # Düzenli bir görevle ilişkili olanlar
    )

    print(f"{len(expired_tasks)} adet görev kontrol ediliyor...")
    
    tasks_closed = 0
    if len(expired_tasks) == 0:
        print("Kapatılacak görev yok.")
        return
    
    for task in expired_tasks:
        # Görevin açık kalma süresini kontrol et
        time_since_deadline = (current_time - task.deadline).days
        if time_since_deadline >= task.scheduledTask.numberOfDayOpen:
            task.statu = close_status
            task.closed_date = current_time
            task.save()
            LoglaToFile("Görev otomatik kapatıldı: " + task.title+"task.id:"+str(task.id))
            if task.responsible_user:
                send_sms(task.responsible_user.phone_number, f"{task.title} görevi otomatik olarak kapatıldı.")
                send_sms("5326179630", f"{task.title} görevi otomatik olarak kapatıldı.")
            tasks_closed += 1

    print(f"{tasks_closed} görev otomatik olarak kapatıldı.")

def task_statu_notification():
    """
    gorevden bir gün sonra bildirim gönderir. 
    whatsapp mesajı gönderir. mesaj içerisinde butonlarla statu güncelleme yapılabilir.
    """
    # Dün için başlangıç ve bitiş zamanlarını hesaplayalım
    today = datetime.datetime.now()
    yesterday_start = datetime.datetime(today.year, today.month, today.day) - datetime.timedelta(days=1)
    yesterday_end = datetime.datetime(today.year, today.month, today.day)
    
    print("yesterday_start:",yesterday_start)
    print("yesterday_end:",yesterday_end)
    # Dün deadline'ı kapsayan taskları filtreleme
    tasks = Gorevler.objects.filter(deadline__gte=yesterday_start, deadline__lt=yesterday_end,closed_date__isnull=True)

    #tasks = Gorevler.objects.all()
    
    print("Görevler kontrol ediliyor...")
    print(f"{len(tasks)} adet görev kontrol ediliyor...")

    for task in tasks:
        if task.responsible_user:
            try:
                whatsappTaskMessage(task.responsible_user.employee.telephone,task)
                whatsappTaskMessage("05326179630",task)
            except Exception as e:
                print(f"whatsapp mesajı gönderilemedi. hata:{e}")
            
    
if __name__ == "__main__":
    task_statu_notification()
