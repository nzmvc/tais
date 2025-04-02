import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from gorevler.models import Gorevler
from gorevler.forms import GorevForm
from django.contrib.messages import get_messages

@pytest.mark.django_db
def test_gorevEkle_get_request():
    client = Client()
    user = User.objects.create_user(username='testuser', password='12345')
    client.login(username='testuser', password='12345')
    session = client.session
    session['company'] = 1
    session.save()
    
    response = client.get(reverse('gorevEkle'))
    
    assert response.status_code == 200
    assert isinstance(response.context['form'], GorevForm)
    assert 'gorevEkle.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_gorevEkle_post_request_valid_form(mocker):
    client = Client()
    user = User.objects.create_user(username='testuser', password='12345')
    client.login(username='testuser', password='12345')
    session = client.session
    session['company'] = 1
    session.save()
    
    mocker.patch('gorevler.views.getSettings', return_value=True)
    mocker.patch('gorevler.views.send_sms')
    mocker.patch('gorevler.views.whatsappMessage')
    mocker.patch('gorevler.views.Logla')
    
    data = {
        'title': 'Test Gorev',
        'smsGonder': 'True',
        'responsible_user': user.id,
        'start_date': '2023-01-01',
        'deadline': '2023-01-10'
    }
    
    response = client.post(reverse('gorevEkle'), data)
    
    assert response.status_code == 302
    assert response.url == '/gorevler/gorevListele/aktif'
    assert Gorevler.objects.count() == 1
    gorev = Gorevler.objects.first()
    assert gorev.title == 'Test Gorev'
    assert gorev.company_id == 1
    assert gorev.open_user == user

@pytest.mark.django_db
def test_gorevEkle_post_request_invalid_form():
    client = Client()
    user = User.objects.create_user(username='testuser', password='12345')
    client.login(username='testuser', password='12345')
    session = client.session
    session['company'] = 1
    session.save()
    
    data = {
        'title': '',
        'smsGonder': 'True',
        'responsible_user': user.id,
        'start_date': '2023-01-01',
        'deadline': '2023-01-10'
    }
    
    response = client.post(reverse('gorevEkle'), data)
    
    assert response.status_code == 200
    assert 'gorevEkle.html' in [t.name for t in response.templates]
    assert Gorevler.objects.count() == 0
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0