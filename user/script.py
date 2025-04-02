from gorevler.models import Gorevler,Reminder
import datetime

now = datetime.datetime.now()
gorevler = Gorevler.objects.filter(start_date__gt = now )

for gorev in gorevler:
    reminders = Reminder.objects.filter(gorev = gorev)
    for reminder in reminders: 
        if reminder.reminder_date < now:
            print("hatırlatma tarihi geçmiş")
        if reminder.time_type == '1': # dakika
            deltaTime = datetime.timedelta(minutes=reminder.time)
        elif reminder.time_type == '2': # saat
            deltaTime = datetime.timedelta(hours=reminder.time)
        elif reminder.time_type == '3': # gün
            deltaTime = datetime.timedelta(days=reminder.time)
        elif reminder.time_type == '4': # hafta
            deltaTime = datetime.timedelta(weeks=reminder.time)
        elif reminder.time_type == '5': # ay
            deltaTime = datetime.timedelta(weeks=reminder.time*4)

        if  0 < gorev.start_date - now < deltaTime :
            print("uyarı gönderilecek")
            print(gorev.title)