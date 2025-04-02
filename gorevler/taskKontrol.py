import sqlite3
from sqlite3 import Error
from datetime import datetime,timedelta, timezone

import requests


def create_connection(dbname):
    conn = None
    try:
        conn = sqlite3.connect(dbname)
        print("bağlantı sağlandı")
    except Error as e:
        print(e)
    return conn


turkce=[("Ç","C"),("Ö","O"),("İ","I"),("Ş","S"),("Ü","U"),("Ğ","G")]
def sms_icerik_duzekt(str):
    str = str.upper()
    for ch in turkce:
        str = str.replace(ch[0],ch[1])
    return str

def Logla(message):

    filename = "log_task_control.txt"                      
        
    with open(filename,"a", encoding="utf-8") as d:
        d.write( f'{datetime.now()} {message} \r' )




############################################################################
####################### SEND _SMS_       #################################
############################################################################


#<?xml version='1.0' encoding='utf-8'?>
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
      
        print("sms donus:",req_sms.text[:2])
        #messages.info(request,f"SMS :{sms_donus[req_sms.text[:2]]}")
        Logla(f"{gsm_no} numarasına sms gonderildi sonu:{sms_donus[req_sms.text[:2]]}")

    except Exception as e:
        print("sms hata:",e)
        Logla(f"{gsm_no} numarasına sms gonderiminde hata yaşandı hata: {e} ")
       
def deadlineReminder(conn):
    # deadline a 3 gun kala hatirlatma mesaji gonder
    print("deadlineReminder")
    cur = conn.cursor()

    now = datetime.now()
    three_days_later = now + timedelta(days=3)
    three_days_later_start = three_days_later.replace(hour=0, minute=0, second=0, microsecond=0)
    three_days_later_end = three_days_later_start + timedelta(days=1)

    start_date = three_days_later_start.strftime('%Y-%m-%d')
    end_date = three_days_later_end.strftime('%Y-%m-%d')

    query       = f"select telephone ,u.first_name,u.last_name, g.deadline,g.title,g.id,g.secret from gorevler_gorevler g, auth_user u ,user_employee e where g.company_id=1 and g.responsible_user_id = u.id and u.id =e.id and g.closed_date is NULL and  \"{start_date} 00:00:00\" < g.deadline and  g.deadline <  \"{end_date} 00:00:00\"  "
    test_query  = f"select telephone ,u.first_name,u.last_name, g.deadline,g.title,g.id,g.secret from gorevler_gorevler g, auth_user u ,user_employee e where g.company_id=1 and g.responsible_user_id = u.id and u.id =e.id and g.closed_date is NULL  and responsible_user_id = 2"
    
    Logla(f"query:{query}")

    print("quert:", query) 
    cur.execute(test_query)
    rows = cur.fetchall()

    for row in rows:
        print("row:",row)
        tel = row[0]
        print("tel:",tel)
        msg = f"Merhaba {row[1]}, {row[4]} başlıklı görevinizin bitiş tarihi yaklaşmaktadır. Lütfen görevinizi tamamlayınız. https://demo.toyu.app/gorevler/taskViewWithSecret/{row[5]}/{row[6]}"
        Logla(f"msg:{msg}")
        send_sms(tel,msg)

def deadlineOver(conn):
    # deadline geçen görevler için hatırlatma mesajı gönder
    print("deadlineOver")
    cur = conn.cursor()

    now = datetime.now()
    eski = now - timedelta(days=1)

    #query = f"select telephone ,u.first_name,u.last_name, g.deadline,g.title,g.id,g.secret from gorevler_gorevler g, auth_user u ,user_employee e where g.company_id=1 and g.responsible_user_id = u.id and u.id =e.id and g.closed_date is NULL and  g.deadline < \"{now.strftime('%Y-%m-%d %H:%M:%S')}\" and  \"{eski.strftime('%Y-%m-%d %H:%M:%S')}\" < g.deadline"
    query = f"select telephone ,u.first_name,u.last_name, g.deadline,g.title,g.id,g.secret from gorevler_gorevler g, auth_user u ,user_employee e where g.company_id=1 and g.responsible_user_id = u.id and u.id =e.id and g.closed_date is NULL and  g.deadline < \"{now.strftime('%Y-%m-%d %H:%M:%S')}\"  and \"{eski.strftime('%Y-%m-%d %H:%M:%S')}\" < g.deadline and responsible_user_id = 2"
    Logla(f"query:{query}")
    print("quert:", query) 
    cur.execute(query)
    rows = cur.fetchall()

    for row in rows:
        print("row:",row)
        tel = row[0]
        print("tel:",tel)
        msg = f"Merhaba {row[1]}, {row[4]} başlıklı görevinizin bitiş tarihi geçmiştir. Lütfen görevinizi tamamlayınız. https://demo.toyu.app/gorevler/taskViewWithSecret/{row[5]}/{row[6]}"
        Logla(f"msg:{msg}")
        send_sms(tel,msg)

def main():
    #database = "/home/nazimavci/test.toyu/db.sqlite3"
    database = "../db.sqlite3"
    Logla("Task Kontrol başladı")
    # create a database connection
    try:
        # Veritabanı bağlantısını açma
        with sqlite3.connect(database) as conn:
            
            deadlineReminder(conn)          # deadline a 3 gun kala hatirlatma mesaji gonder
            deadlineOver(conn)              # deadline geçen görevler için hatırlatma mesajı gönder

    except sqlite3.Error as e:
        print("SQLite hatası:", e)
        Logla(f"SQLite hatası:{e}")
    
    Logla("Task Kontrol bitti")

if __name__ == '__main__':
    main()