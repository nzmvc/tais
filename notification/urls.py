from django.contrib import admin
from django.urls import path
from . import views

app_name="notification"

urlpatterns = [
    path('notificationAdd/',views.notificationAdd,name='notificationAdd'),
    #path('notificationDelete/<int:id>',views.notificationDelete,name='notificationDelete'),
    path('notificationList/',views.notificationList,name='notificationList'),
    #path('notificationView/<int:id>',views.notificationView,name='notificationView'),
    #path('notificationUpdate/<int:id>',views.notificationUpdate,name='notificationUpdate'),

    path('whatsappMessage/',views.whatsappMessage,name='whatsappMessage'),
    path('whatsappWebHook/',views.whatsappWebHook,name='whatsappWebHook'),
]