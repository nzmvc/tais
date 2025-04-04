import uuid
from django.shortcuts import render,redirect,get_object_or_404
import openai
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import os
from decouple import config
from user.views import Logla
from .forms import ChatbotForm, UploadedFileForm
from .models import Chatbot, UploadedFile, ChatbotSession, ChatMessage
from django.contrib import messages
import datetime

def LoglaChat(request,message):

    filename = "log_chat.txt"
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
        
def get_client_ip(request):
    """ Kullanıcının IP adresini al """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_or_create_session(chatbot, request):
    """ Kullanıcının mevcut session'ı varsa getir, yoksa yeni bir tane oluştur """
    data = json.loads(request.body)
    session_id = data.get("session_id", None)
    print("client dan gelen session_id:", session_id)
    
    
    if session_id:
        session = ChatbotSession.objects.filter(session_id=session_id, chatbot=chatbot).first()
        if session:
            session.last_active = datetime.datetime.now()
            session.save()
            return session

    # Yeni session oluştur
    session = ChatbotSession.objects.create(
        chatbot=chatbot,
        session_id=uuid.uuid4(),
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    print("yeni session olusturuldu", session.id)
    # Django session'a session_id'yi kaydet
    request.session["session_id"] = str(session.session_id)

    return session

def save_chat_message(session, role, content, tokens=0):
    """ Kullanıcı veya asistanın mesajlarını kaydeder """
    message = ChatMessage.objects.create(
        session=session,
        role=role,
        content=content,
        tokens=tokens
    )
    return message

def get_chat_history(session):
    """ Oturuma ait tüm mesajları getirir """
    return ChatMessage.objects.filter(session=session).order_by("created_at")

# OpenAI istemcisi oluştur
client = OpenAI(api_key=config("OPENAI_TEST_KEY"))
ASSISTANT_ID = config("ASSISTANT_ID")  # Daha önceden oluşturulmuş asistan ID'si
VECTOR_STORE_ID = config("VECTOR_STORE_ID")

@csrf_exempt
def chatbot_api(request, api_key):
    #print("chatbot_api çalıştı")
    #print("api_key:", api_key)

    if request.method == "POST":
        #print("POST isteği alındı")
        
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            
            chatbot = Chatbot.objects.get(api_key=api_key)
            
            # session alınır yada create edilir
            session = get_or_create_session(chatbot, request)

            # Kullanıcı mesajını kaydet
            save_chat_message(session, role="user", content=message)
            
            if not chatbot.assistant_id or not chatbot.vector_store_id:
                print("Chatbot henüz yapılandırılmamış.")
                return JsonResponse({"error": "Chatbot henüz yapılandırılmamış."}, status=400)

            client = OpenAI(api_key=config("OPENAI_TEST_KEY"))

            # OpenAI Thread oluştur
            thread = client.beta.threads.create()

            # Bu sessiondaki geçmiş mesajları alıyoruz
            chat_history = get_chat_history(session)
            
            # Geçmiş mesajları thread e ekliyoruz gönder
            for chat in chat_history:
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role=chat.role,
                    content=chat.content
                )
                
            # Son mesaj threade ekle
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message
            )

            # Asistanı çalıştır
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=chatbot.assistant_id
            )

            # Run işleminin tamamlanmasını bekle
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Yanıtı al
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            reply = messages.data[0].content[0].text.value  # Yeni API'ye göre çıktı formatı

            # Chatbot yanıtını kaydet
            save_chat_message(session, role="assistant", content=reply)
            
            
            print("reply:", reply)
            return JsonResponse({"reply": reply , "session_id": str(session.session_id)})

        except Chatbot.DoesNotExist:
            print("Chatbot bulunamadı.")
            return JsonResponse({"error": "Chatbot bulunamadı."}, status=404)

        except Exception as e:
            print("Hata:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Geçersiz istek."}, status=400)



@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            print("user_message:", user_message)
            
            if not user_message:
                return JsonResponse({"error": "Message field is required."}, status=400)

            # Yeni bir thread oluşturmak yerine, belirli bir thread ID kullan veya oluştur.
            # Örneğin, eğer kullanıcı ID'si varsa, onun için bir thread kaydetmelisin.
            thread = client.beta.threads.create()  # Burayı veritabanında kontrol edip kullanıcıya özel yapabilirsin.
            
            print("thread:",thread)
            
            # Mesajı gönder
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )

            # Asistanın yanıt vermesi için çalıştır
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID  # Burada asistan ID'sini kullan
            )

            # Yanıt tamamlanana kadar bekle
            while True:
                retrieved_run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if retrieved_run.status == "completed":
                    break
            print("retrieved_run:",retrieved_run)
            # Yanıtı al
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            bot_reply = "\n".join(
                content_block.text.value for message in messages.data if message.role == "assistant"
                for content_block in message.content if content_block.type == "text"
            )
            
            """print("bot_reply:", bot_reply)
            print("TTS çalışacak")
            # OpenAI Text-to-Speech (TTS) API ile sesi oluştur
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=bot_reply
            )

            print("TTS çalıştı. ses dosyası kaydedilecek")
            # Ses dosyasını kaydet
            audio_file_path = "media/audio_response.mp3"
            with open(audio_file_path, "wb") as audio_file:
                audio_file.write(speech_response.read())  # .audio yerine .read() kullan!

            print( "ses dosyası kaydedildi")"""

            LoglaChat(request,f'Chatbot mesajı: {user_message} Chatbot yanıtı: {bot_reply}')
            return JsonResponse({"reply": bot_reply, "audio_url": f"/media/audio_response.mp3"}, status=200)

        except Exception as e:
            Logla(request,f"chatbot_response hata:{e}")
            return JsonResponse({"error": str(e)}, status=500)
        

    return JsonResponse({"error": "Only POST requests are allowed."}, status=400)

"""
# bilgi dosyalarını yükler ve buradan sorgulama yapar.
# bu dosyaları güncelleyip öğrenimi gennnişletebiliriz.

@csrf_exempt
def chatbot_response(request):
    print("chatbot_response çalıştı")
    client = OpenAI(api_key=config("OPENAI_TEST_KEY"))
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("data:", data)
            
            user_message = data.get("message")
            print("user_message:", user_message)

            if not user_message:
                return JsonResponse({"error": "Message field is required."}, status=400)

            # Step 1: Create a new Assistant with File Search Enabled
            assistant = client.beta.assistants.create(
                name="TOYU Kullanıcı Asistanı",
                instructions="Sen TOYU satış uzmanısın, teknik detaylara sahipsin ve müşterilere yardımcı oluyorsun.",
                model="gpt-3.5-turbo",  # Bu da başka bir seçenek
                tools=[{"type": "file_search"}],
            )

            
            # Step 2: Upload files and add them to a Vector Store
            vector_store = client.beta.vector_stores.create(name="TOYU satış uzmanı")

            # Ready the files for upload to OpenAI
            #file_paths = ["support_files/toyu_genel_ozellikler.txt", "support_files/uretim_modul_kullanici_kilavuz.txt", "support_files/faq.txt"]
            
            file_paths = [
                os.path.join(settings.MEDIA_ROOT, "support_files", "toyu_genel_ozellikler.txt"),
                os.path.join(settings.MEDIA_ROOT, "support_files", "uretim_modul_kullanici_kilavuz.txt"),
                os.path.join(settings.MEDIA_ROOT, "support_files", "faq.txt"),
            ]
            
            file_streams = [open(path, "rb") for path in file_paths]

            # Use the upload and poll SDK helper to upload the files, add them to the vector store,
            # and poll the status of the file batch for completion.
            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )
            
            print("Vector Store ID:", vector_store.id)
            # Print file batch status to verify
            print(file_batch.status)
            print(file_batch.file_counts)

            # Step 3: Update the assistant to use the new Vector Store
            assistant = client.beta.assistants.update(
                assistant_id=assistant.id,
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            )
            
            # Step 4: Create a thread
            thread = client.beta.threads.create()

            # Send user message in the thread
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )

            # Run the thread and wait for the response
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            # Wait for the run to complete
            while True:
                retrieved_run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if retrieved_run.status == "completed":
                    break
                # You can adjust the wait time as necessary
                # time.sleep(1)

            # Retrieve messages from the thread
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            
            bot_reply = ""
            for message in messages.data:
                print("---message:", message)
                if message.role == "assistant":
                    print("message.content:", message.content)
                    for content_block in message.content:  # İçerik bloklarını tek tek al
                        print("content_block:", content_block)
                        if content_block.type == "text":  # Eğer metin içeriğiyse
                            bot_reply += content_block.text.value + "<br>"

            print("bot_reply:", bot_reply)
            return JsonResponse({"reply": bot_reply}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            print("Hata:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed."}, status=400)"""

def chat_popup(request):
    return render(request, "chat_popup.html")

def chat(request):
    return render(request, 'chat.html')



@login_required
def create_chatbot(request):
    print("create_chatbot çalıştı")
    if request.method == 'POST':
        form = ChatbotForm(request.POST)
        file_form = UploadedFileForm(request.POST, request.FILES)
        print("form:", form)
        if form.is_valid():
            print("form valid")
            chatbot = form.save(commit=False)
            chatbot.user = request.user  # Kullanıcıyı atıyoruz
            chatbot.company_id = request.session["company"]  # Kullanıcının şirketini atıyoruz
            chatbot.save()
            print("Chatbot oluşturuldu:", chatbot.id)
            Logla(request,f"Chatbot database de oluşturuldu: {chatbot.id}")
            # Dosyalar varsa kaydet
            files = request.FILES.getlist('file')
            for file in files:
                UploadedFile.objects.create(chatbot=chatbot, file=file, created_user=request.user)

            # Dosyaları OpenAI'ye uygun hale getir
            uploaded_files = UploadedFile.objects.filter(chatbot=chatbot)
            file_streams = []
            for uploaded_file in uploaded_files:
                file_path = uploaded_file.file.path  # Django'da dosyanın tam yolunu al
                file_streams.append(open(file_path, "rb"))  # Byte formatında aç
    
            client = OpenAI(api_key=config("OPENAI_TEST_KEY"))
            
            # ADIM 1: Asistan oluşturulur
            assistant = client.beta.assistants.create(
                name        = chatbot.name,
                instructions=chatbot.instructions,
                model       = chatbot.model,  # Bu da başka bir seçenek
                tools       =[{"type": "file_search"}],
                temperature   = chatbot.temperature,
            )
            
            
            if not assistant:
                print("Asistan oluşturulamadı.")
                Logla(request,f"adım 1 OpenAI asistanı oluşturulamadı")
                return JsonResponse({"error": "Asistan oluşturulamadı."}, status=400)
            
            Logla(request,f"adım 1 OpenAI asistanı oluşturuldu: {assistant.id}")
            print("Asistan oluşturuldu:", assistant.id)
            chatbot.assistant_id = assistant.id
            chatbot.save()
            
            # ADIM 2: Vektör deposu oluşturulur
            #vector_store = client.beta.vector_stores.create(name=chatbot.name)
            vector_store = client.vector_stores.create(name=chatbot.name)
            chatbot.vector_store_id = vector_store.id
            chatbot.save()
            print("Vektör deposu oluşturuldu:", vector_store.id) 
            Logla(request,f"Adım 2 vektor deposu oluşturuldu: {vector_store.id}")
            
            # ADIM 3: Dosyaları yükle ve vektör deposuna ekle
            file_batch = client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )
            print("Dosyalar yüklendi ve vektör deposuna eklendi:", file_batch.status)
            Logla(request,f"adım 3 dosyalar yüklendi ve vektör deposuna eklendi: {file_batch.status}")
            
            """assistant = client.beta.assistants.update(
                assistant_id=assistant.id,
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            )"""
            
            # ADIM 4: Asistanı güncelle
            # Asistanı güncelle ve vektör deposunu ekle
            assistant = client.beta.assistants.update(
                assistant_id=assistant.id,
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            )
            Logla(request,f"adım 4 asistan güncellendi: {assistant.id}")
            
            return redirect(f"/chatbot/chatbot_view/{chatbot.id}")
        else:
            print("Form geçersiz:", form.errors)
            Logla(request,f"Form geçersiz: {form.errors}")
            messages.error(request, "Form geçersiz. Lütfen kontrol edin.")
    else:
        form = ChatbotForm()
        file_form = UploadedFileForm()
    
    return render(request, 'create_chatbot_v3.html', {'form': form, 'file_form': file_form})

@login_required
def chatbot_view(request, chatbot_id):
    chatbot = get_object_or_404(Chatbot, id=chatbot_id)
    
    if request.method == 'POST':
        form = ChatbotForm(request.POST, instance=chatbot)
        
        if form.is_valid():
            form.save()
            return redirect('chatbot_detail', chatbot.id)
    else:
        form = ChatbotForm(instance=chatbot)
    
    return render(request, 'chatbot_view_v3.html', {'form': form, 'chatbot': chatbot})


@login_required
def chatbot_list(request):
    chatbots = Chatbot.objects.filter(user=request.user)
    return render(request, 'chatbot_list.html', {'chatbots': chatbots})

@login_required
def chatbot_update(request, chatbot_id):
    chatbot = get_object_or_404(Chatbot, id=chatbot_id)
    
    if request.method == 'POST':
        form = ChatbotForm(request.POST, instance=chatbot)
        
        if form.is_valid():
            form.save()
            messages.info(request,"guncelleme yapıldı")
            Logla(request,f"Chatbot local database güncellendi: {chatbot.id}")
            
            #TODO: openai'den asistanı güncelleme işlemi
            client = OpenAI(api_key=config("OPENAI_TEST_KEY"))
            try:
                response = client.beta.assistants.update(
                    assistant_id=chatbot.assistant_id,
                    instructions=chatbot.instructions,
                    model=chatbot.model,
                    temperature=chatbot.temperature
                    
                )
                print("Asistan güncellendi:", response)
                Logla(request,f"OpenAI asistanı güncellendi: {response.id}")
                messages.info(request,"OpennAI asistan güncellendi")
            except e:
                Logla(request,f"OpenAI asistanı güncellenemedi: {e}")
                messages.error(request,"Asistan güncellenemedi. Hata: "+str(e))
                print("OpenAI Assistant Güncelleme Hatası:", e)
            return redirect('chatbot_view', chatbot.id)
    else:
        form = ChatbotForm(instance=chatbot)
    
    return render(request, 'chatbot_update.html', {'form': form, 'chatbot': chatbot})

@login_required
def chatbot_delete(request, chatbot_id):
    
    chatbot = get_object_or_404(Chatbot, id=chatbot_id)
    
    #TODO: openai'den asistanı silme işlemi
    client = OpenAI(api_key=config("OPENAI_TEST_KEY"))
    try:

        response = client.beta.assistants.delete(chatbot.assistant_id)
        print("Asistan silindi:", response)
        messages.info(request,"OpennAI asistan silindi") 
        Logla(request,f"OpenAI asistanı silindi: {response.id}")
        
        # Silme işlemi başarılıysa, chatbot'u sil
        chatbot.delete()
        print("Chatbot silindi:", chatbot.id)
        Logla(request,f"Chatbot local database silindi: {chatbot.id}")
        messages.info(request,"TAIS db den asistan silindi") 

    except Exception as e:
        print("OpenAI Assistant Silme Hatası:", e)
        Logla(request,f"OpenAI asistanı silinemedi: {e}")
        messages.error(request,"Asistan silinemedi. Hata: "+str(e))

    return redirect('/chatbot/chatbot_list')
    