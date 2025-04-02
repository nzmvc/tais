from django.contrib import admin
from django.urls import path
from . import views

app_name="gorevler"

urlpatterns = [
    path('ilkgorevEkle/',views.ilkgorevEkle,name='ilkgorevEkle'),
    path('gorevEkle/',views.gorevEkle,name='gorevEkle'),
    path('gorevSil/<int:id>',views.gorevSil,name='gorevSil'),
    path('gorevListele/<str:ap>',views.gorevListele,name='gorevListele'),
    path('gorevGoster/<int:id>',views.gorevGoster,name='gorevGoster'),
    path('gorevGuncelle/<int:id>',views.gorevGuncelle,name='gorevGuncelle'),
    path('taskViewWithSecret/<int:gorev_id>/<str:secret>',views.taskViewWithSecret,name='taskViewWithSecret'),
    path('gorevStatuUpdate/<int:gorev_id>/<int:statu_id>/<str:secret>',views.gorevStatuUpdate,name='gorevStatuUpdate'),

    path('duzenliGorevTanimla/',views.duzenliGorevTanimla,name='duzenliGorevTanimla'),
    path('duzenliGorevSil/<int:id>',views.duzenliGorevSil,name='duzenliGorevSil'),
    path('duzenliGorevListele/',views.duzenliGorevListele,name='duzenliGorevListele'),
    path('duzenliGorevGoster/<int:id>',views.duzenliGorevGoster,name='duzenliGorevGoster'),
    path('duzenliGorevGuncelle/<int:id>',views.duzenliGorevGuncelle,name='duzenliGorevGuncelle'),
    path('duzenliGorevRapor/<int:year>/<int:month>/<str:type>',views.duzenliGorevRapor,name='duzenliGorevRapor'),
    
    path('gorevStatuAdd/',views.gorevStatuAdd,name='gorevStatuAdd'),
    path('gorevStatuList/',views.gorevStatuList,name='gorevStatuList'),
    path('gorevStatuCustomUpdate/<int:id>',views.gorevStatuCustomUpdate,name='gorevStatuUpdate'),
    path('gorevStatuDelete/<int:id>',views.gorevStatuDelete,name='gorevStatuDelete'),


    path('gorevSmsGonder/<int:gorev_id>',views.gorevSmsGonder,name='gorevSmsGonder'),
    
    path('rapor_gorev/',views.rapor_gorev,name='rapor_gorev'),
    #path('acilan_gorev/',views.acilan_gorev,name='acilan_gorev'),
    path('gorev_takvim_data/',views.gorev_takvim_data,name='gorev_takvim_data'),
    path('takvim_task/',views.takvim_task,name='takvim_task'),
    
]