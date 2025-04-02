# Base image olarak Python 3.9 kullanıyoruz
FROM python:3.9

# Çalışma dizinini ayarlıyoruz
WORKDIR /taisapp

# Bağımlılıkları yüklemek için requirements.txt dosyasını kopyalıyoruz
COPY requirements.txt /taisapp/
RUN pip install --no-cache-dir -r requirements.txt

# Projenin tüm dosyalarını kopyalıyoruz
COPY . /taisapp/

# Django uygulamasını başlatmak için komut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Dockerfile dosyasını build etmek için aşağıdaki komutu çalıştırın
# docker build -t django-docker .
# docker run -p 8000:8000 django-docker

# http://localhost:8000 adresine giderek uygulamayı görebilirsiniz
