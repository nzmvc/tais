import datetime
from django.utils.timezone import now
import sys,os,django,requests

# Proje kök dizinini Python yoluna ekleyin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

script_dir = os.path.dirname(os.path.abspath(__file__))

# Proje kök dizinini ekleyin
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

# Django ayarlarını kullanabilmek için ortam değişkenlerini ayarlayın
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toyu.settings')
django.setup()

from gorevler.models import DuzenliGorevTanim, Gorevler


############################################
hostname =  f'https://demo.toyu.app/'
############################################
def LoglaToFile(message):

    filename = "log_task_kontrol.txt"

    with open(filename,"a", encoding="utf-8") as d:
        d.write( f'{datetime.datetime.now()}-message:{message} \n\r' )

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
    
    #gsm_mesaj = sms_icerik_duzekt(gsm_mesaj)
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
        
        

"""
def gorev_olustur(scheduleTask):
    # Görev başlangıç tarihi ve frekansı
    start_date = scheduleTask.start_date  # Görevin başlangıç tarihi
    frequency_days = scheduleTask.frequency  # x günde bir oluşturulacak
    numberOfDayCreate = scheduleTask.numberOfDayCreate # kaç gün önce oluşturulacak
    today = datetime.date.today()
    
    # start_date'den itibaren bugün için hangi tarihin oluşturulması gerektiğini hesapla
    days_since_start = (today - start_date).days
    print("days_since_start:",days_since_start)
    
    if days_since_start < 0:
        LoglaToFile(f"Bugün için görev oluşturulamaz, start_date {scheduleTask.start_date} gelecekte.")
        print("Bugün için görev oluşturulamaz, start_date gelecekte.")
        return

    # Bugün ile x günde bir olan döngünün en yakın tarihini bul
    next_task_date = start_date + datetime.timedelta(days=(days_since_start // frequency_days) * frequency_days)
    next_task_date = next_task_date.strftime('%Y-%m-%d 00:00:01') # bu önemli kontrolde problem olmaması için 

    print("next_task_date:",next_task_date)
    
    # Daha önce böyle bir görev var mı kontrol et
    existing_task = Gorevler.objects.filter(scheduledTask=scheduleTask, deadline=next_task_date).exists()
                                                                    
    #task yoksa ve oluşturulacak tarih sistemdebelirtilen  gün sayısı kadar önceyse oluştur
    if not existing_task and next_task_date <= today + datetime.timedelta(days=numberOfDayCreate):
        # Yeni görev oluştur
        new_task = Gorevler()
        new_task.scheduledTask = scheduleTask
        new_task.title = scheduleTask.title
        new_task.description = scheduleTask.description
        if scheduleTask.responsible_user:
            new_task.responsible_user = scheduleTask.responsible_user
        if scheduleTask.department:
            new_task.department = scheduleTask.department
        new_task.deadline = next_task_date

        new_task.save()

        LoglaToFile(f"Yeni görev oluşturuldu: {scheduleTask.title}, {next_task_date}")
    else:
        LoglaToFile(f"Bugün için görev zaten oluşturulmuş: {scheduleTask.title}")
""" 
    
    
def gunluk_task_olustur(scheduleTask):
    print("gunluk_task_olustur fonksiyonu çalıştı",scheduleTask)
    if scheduleTask.numberOfDayCreate and scheduleTask.start_date: # ne kadar gün önce oluşturulacak tanımlanndıysa
                
        # Görev başlangıç tarihi ve frekansı
        start_date = scheduleTask.start_date  # Görevin başlangıç tarihi
        frequency_days = scheduleTask.frequency  # x günde bir oluşturulacak
        numberOfDayCreate = scheduleTask.numberOfDayCreate # kaç gün önce oluşturulacak
        today = datetime.date.today()
        
        # start_date'den itibaren bugün için hangi tarihin oluşturulması gerektiğini hesapla
        days_since_start = (today - start_date).days 
        print("days_since_start:",days_since_start)
        
        if days_since_start + frequency_days < 0:
            LoglaToFile(f"Bugün için görev oluşturulamaz, start_date {scheduleTask.start_date} gelecekte.")
            print("Bugün için görev oluşturulamaz, start_date gelecekte.")
            return        
        
        # Bugün ile x günde bir olan döngünün en yakın tarihini bul
        nextTaskDate = start_date + datetime.timedelta(days=(days_since_start // frequency_days) * frequency_days)
        nextTaskDate = nextTaskDate.strftime('%Y-%m-%d 23:59:00') # bu önemli kontrolde problem olmaması için 
        nextTaskDate = datetime.datetime.strptime(nextTaskDate, '%Y-%m-%d %H:%M:%S')
        
        print("next_task_date:",nextTaskDate)
        
        max_task_count = 25  # sonsuz döngüye düşmesin diye sınırlandırıldı
        
        # dongü ile önceden açılacak gün sayısı ve frekansa göre task oluşturulacak
        # max_task_count ile sonsuz döngüye düşmesin diye sınırlandırıldı
        
        #TODO: burada bir hata var ayın 29 unda 28 inin tasklarını oluşturdu ???? fakat aşağıdaki kosuşda doğru çalışmadı
        #while nextTaskDate >= datetime.datetime.today() and nextTaskDate < datetime.datetime.today() + datetime.timedelta(days=scheduleTask.numberOfDayCreate):
        
        while nextTaskDate < datetime.datetime.today() + datetime.timedelta(days=scheduleTask.numberOfDayCreate):
            print("---while döngüsü")
            max_task_count -= 1
            
            # oluşsturulacak task daha önce tanımlanmış mı kontrol et
            nextTask = Gorevler.objects.filter(scheduledTask=scheduleTask,deadline=nextTaskDate)
            print("nextTask:",nextTask)
            
            if not nextTask:# tanımlanmamışsa oluştur
                print("Task oluşturulacak")
                newTask = Gorevler()
                newTask.scheduledTask = scheduleTask
                newTask.title = scheduleTask.title
                newTask.description = scheduleTask.description
                if scheduleTask.responsible_user:
                    newTask.responsible_user = scheduleTask.responsible_user
                if scheduleTask.department:
                    newTask.department = scheduleTask.department
                newTask.deadline = nextTaskDate
                
                newTask.save() 
                print(f"deadlinne: {nextTaskDate} Task oluşturuldu id :{newTask}")
                
                print("sms gonderilecek")
                
                if scheduleTask.responsible_user:
                    gsm_message = f"Otomatik görev-{newTask.title[0:20]} {hostname}gorevler/taskViewWithSecret/"+ str(newTask.id) +"/"+newTask.secret
                    send_sms(newTask.responsible_user.employee.telephone,gsm_message)
                    #send_sms("5326179630", gsm_message)
                
                
                LoglaToFile(f"Task oluşturuldu {scheduleTask.title}, {nextTaskDate} , task.id:{scheduleTask.id}")
            else:
                print("Task zaten oluşturulmuş")
                #LoglaToFile(f"Task zaten oluşturulmuş .duzenli gorev \"{scheduleTask.title}\" ")
            
            # frekansa göre bu tasktan sonraki task tarihi bulunur. while döngüsü ile devam edilir
            nextTaskDate = nextTaskDate + datetime.timedelta(days=scheduleTask.frequency)
            if max_task_count == 0:
                print("sonsuz döngüye düşme riski var dongunden çıkıldı")
                LoglaToFile(f"sonsuz döngüye düşme riski var dongunden çıkıldı")
                break  
            
        # TODO: günlük tasklarda frekans 1 ile hergün 2 ise iki günde bir 3 ise 3 günde bir kontrolü yapılmalı
        #gorev olusturulduktan sonra duzenli gorev tanimindaki numberOfDayCreate degeri kadar gun sonrasina gorev olusturulur
    else:
        LoglaToFile(f"numberOfDayCreate tanımlanmamış {scheduleTask.title}")
        print("numberOfDayCreate tanımlanmamış")

def weekly_task_olustur(scheduleTask):
    print("weekly_task_olustur fonksiyonu çalıştı", scheduleTask)
    if scheduleTask.numberOfDayCreate and scheduleTask.start_date:  # Kaç gün önce oluşturulacağı tanımlanmışsa

        # Görev başlangıç tarihi, frekansı ve haftanın günleri
        start_date = scheduleTask.start_date  # Görevin başlangıç tarihi
        frequency_weeks = scheduleTask.frequency  # X haftada bir oluşturulacak
        numberOfDayCreate = scheduleTask.numberOfDayCreate  # Kaç gün önce oluşturulacak
        days_of_week = scheduleTask.days_of_week  # Haftanın hangi günleri seçilmiş (ör. [1, 3, 5])
        today = datetime.date.today()

        # Bugün ile start_date arasındaki fark
        days_since_start = (today - start_date).days
        print("days_since_start:", days_since_start)

        if days_since_start < 0:
            LoglaToFile(f"Bugün için görev oluşturulamaz, start_date {scheduleTask.start_date} gelecekte.")
            print("Bugün için görev oluşturulamaz, start_date gelecekte.")
            return

        # Başlangıç tarihinden itibaren en yakın haftanın günlerini bul
        current_week_start = start_date + datetime.timedelta(
            days=(days_since_start // (frequency_weeks * 7)) * (frequency_weeks * 7)
        )

        max_task_count = 15  # Sonsuz döngüyü önlemek için sınır

        for day_offset in range(0, frequency_weeks * 7 * max_task_count, 7): #
            for day in days_of_week:
                day = int(day)
                nextTaskDate = current_week_start + datetime.timedelta(days=day_offset + day - 1)
                
                if nextTaskDate < today or nextTaskDate > today + datetime.timedelta(days=numberOfDayCreate):
                    continue

                nextTaskDatetime = datetime.datetime.combine(nextTaskDate, datetime.time(23, 59))

                # Oluşturulacak görev daha önce tanımlanmış mı kontrol et
                nextTask = Gorevler.objects.filter(
                    scheduledTask=scheduleTask, deadline=nextTaskDatetime
                )
                print("nextTask:", nextTask)

                if not nextTask:  # Tanımlanmamışsa oluştur
                    print("Task oluşturulacak")
                    newTask = Gorevler()
                    newTask.scheduledTask = scheduleTask
                    newTask.title = scheduleTask.title
                    newTask.description = scheduleTask.description

                    if scheduleTask.responsible_user:
                        newTask.responsible_user = scheduleTask.responsible_user
                    if scheduleTask.department:
                        newTask.department = scheduleTask.department
                    newTask.deadline = nextTaskDatetime

                    newTask.save()
                    print(f"deadline: {nextTaskDatetime} Task oluşturuldu id: {newTask.id}")
                    print("sms gonderilecek")

                    if scheduleTask.responsible_user:
                        gsm_message = f"Otomatik görev-{newTask.title[0:20]} {hostname}gorevler/taskViewWithSecret/"+ str(newTask.id) +"/"+newTask.secret
                        send_sms(newTask.responsible_user.employee.telephone,gsm_message)
                        #send_sms("5326179630", gsm_message)
                
                    LoglaToFile(f"Task oluşturuldu {scheduleTask.title}, {nextTaskDatetime}, task.id: {newTask.id}")
                else:
                    print("Task zaten oluşturulmuş")
                    LoglaToFile(f"Task zaten oluşturulmuş: \"{scheduleTask.title}\"")

    else:
        LoglaToFile(f"numberOfDayCreate tanımlanmamış {scheduleTask.title}")
        print("numberOfDayCreate tanımlanmamış")

def monthly_task_olustur(scheduleTask):
    today = now().date()
    counter = 0
    yearOfMonth = today
    
    if scheduleTask.numberOfDayCreate:
        
        while yearOfMonth <= today + datetime.timedelta(days=scheduleTask.numberOfDayCreate):
            
            counter += 1
            if counter > 10:     # Sonsuz döngüyü önlemek için sınır
                break
            
            current_month_start = yearOfMonth.replace(day=1)
            current_month_end = (current_month_start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)

            days_of_month = scheduleTask.days_of_month or []

            if not days_of_month:
                print(f"Düzenli görevde ayın günleri belirtilmemiş: {scheduleTask}")
                return

            for day in days_of_month:
                print("ayın günü için day:",day)
                try:
                    day = int(day)  # Gün bilgisini integer'a çevir
                    if day < 1 or day > current_month_end.day:
                        print(f"Geçersiz gün: {day}, görev oluşturulmadı.")
                        continue

                    nextTaskDate = current_month_start.replace(day=day)
                    print(f"nextTaskDate hesaplandı: {nextTaskDate}")

                    print("onceden oluşturulabilecek tarih : ",today + datetime.timedelta(days=scheduleTask.numberOfDayCreate) )
                    print(f"nextTaskDate:{nextTaskDate}, today:{today}  nextTaskDate >= today : {nextTaskDate >= today} ")
                    if nextTaskDate >= today and nextTaskDate < today + datetime.timedelta(days=scheduleTask.numberOfDayCreate):
                        nextTask = Gorevler.objects.filter(scheduledTask=scheduleTask, deadline=nextTaskDate).first()

                        if not nextTask:  # Eğer bu tarih için görev zaten yoksa, oluştur
                            newTask = Gorevler(
                                scheduledTask=scheduleTask,
                                title=scheduleTask.title,
                                description=scheduleTask.description,
                                responsible_user=scheduleTask.responsible_user,
                                department=scheduleTask.department,
                                deadline=nextTaskDate
                            )
                            
                            if scheduleTask.responsible_user:
                                newTask.responsible_user = scheduleTask.responsible_user
                            if scheduleTask.department:
                                newTask.department = scheduleTask.department
                    
                            newTask.save()
                            print(f"Görev oluşturuldu: {newTask}")
                            
                            if scheduleTask.responsible_user:
                                gsm_message = f"Otomatik görev-{newTask.title[0:20]} {hostname}gorevler/taskViewWithSecret/"+ str(newTask.id) +"/"+newTask.secret
                                send_sms(newTask.responsible_user.employee.telephone,gsm_message)
                                #send_sms("5326179630", gsm_message)
                    
                        else:
                            print(f"Bu tarih için görev zaten var: {nextTask}")
                            
                except ValueError:
                    print(f"Geçersiz gün formatı: {day}, görev oluşturulmadı.")
                except Exception as e:
                    print(f"Hata oluştu: {e}")
                    
            yearOfMonth = yearOfMonth + datetime.timedelta(days=32)
        
            
def yearly_task_olustur(scheduleTask):
    today = now().date()
    current_year = today.year
    current_month = today.month

    days_of_month = scheduleTask.days_of_month or []

    if not days_of_month:
        print(f"Düzenli görevde ayın günleri belirtilmemiş: {scheduleTask}")
        return

    for day in days_of_month:
        try:
            day = int(day)  # Gün bilgisini integer'a çevir
            if day < 1 or day > 31:
                print(f"Geçersiz gün: {day}, görev oluşturulmadı.")
                continue

            nextTaskDate = datetime.date(current_year, current_month, day)
            print(f"nextTaskDate hesaplandı: {nextTaskDate}")

            if nextTaskDate >= today and nextTaskDate < today + datetime.timedelta(days=scheduleTask.numberOfDayCreate):
                nextTask = Gorevler.objects.filter(scheduledTask=scheduleTask, deadline=nextTaskDate).first()

                if not nextTask:  # Eğer bu tarih için görev zaten yoksa, oluştur
                    newTask = Gorevler(
                        scheduledTask=scheduleTask,
                        title=scheduleTask.title,
                        description=scheduleTask.description,
                        responsible_user=scheduleTask.responsible_user,
                        department=scheduleTask.department,
                        deadline=nextTaskDate
                    )
                    
                    if scheduleTask.responsible_user:
                        newTask.responsible_user = scheduleTask.responsible_user
                    if scheduleTask.department:
                        newTask.department = scheduleTask.department
                    
                    newTask.save()
                    print(f"Görev oluşturuldu: {newTask}")
                    print("sms gonderilecek")

                    if scheduleTask.responsible_user:
                        gsm_message = f"Otomatik görev-{newTask.title[0:20]} {hostname}gorevler/taskViewWithSecret/"+ str(newTask.id) +"/"+newTask.secret
                        send_sms(newTask.responsible_user.employee.telephone,gsm_message)
                        #send_sms("5326179630", gsm_message)
                
                else:
                    print(f"Bu tarih için görev zaten var: {nextTask}")
        except ValueError:
            print(f"Geçersiz gün formatı: {day}, görev oluşturulmadı.")
        except Exception as e:
            print(f"Hata oluştu: {e}")

def create_scheduled_tasks():
    
    #today = datetime.today().strftime('%Y-%m-%d')
    
    scheduleTasks = DuzenliGorevTanim.objects.filter(is_active=True)
    
    for scheduleTask in scheduleTasks: 
        #duzenli tanımlanmış taskların herbiri için kontrol yapılacak
        print("####################################################")
        print("scheduleTask:",scheduleTask)
        
        if scheduleTask.repeat_type == "1": #her gün oluşturulacak görevler için
            print("her gün oluşturulacak görevler için")
            gunluk_task_olustur(scheduleTask)
            #gorev_olustur(scheduleTask)
        elif scheduleTask.repeat_type == "2": # haftalık
            weekly_task_olustur(scheduleTask)
        elif scheduleTask.repeat_type == "3": # aylık
            monthly_task_olustur(scheduleTask)
        elif scheduleTask.repeat_type == "4": # yıllık
            yearly_task_olustur(scheduleTask)
        else:
            LoglaToFile(f"Geçersiz tekrar tipi: {scheduleTask.repeat_type}")
            print("Geçersiz tekrar tipi")


                      
def main():
    
    create_scheduled_tasks()
    
if __name__ == '__main__':
    main()