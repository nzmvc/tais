from django.contrib import admin
from django.urls import path,re_path
from . import views
from django.contrib.auth import views as auth_views #import this


app_name="chatbot"

urlpatterns = [
   

    path('chatbot_response/',views.chatbot_response,name='chatbot_response'),
    path('chat/',views.chat,name='chat'),
    path('chat-popup/', views.chat_popup, name='chat_popup'),
    path('chatbot_list/', views.chatbot_list, name='chatbot_list'),
    path('create_chatbot/', views.create_chatbot, name='create_chatbot'),
    path('chatbot_update/<str:chatbot_id>/', views.chatbot_update, name='chatbot_update'),
    path('chatbot_delete/<str:chatbot_id>/', views.chatbot_delete, name='chatbot_delete'),
    path('chatbot_view/<str:chatbot_id>/', views.chatbot_view, name='chatbot_view'),
    
 
    path("api/chatbot/<uuid:api_key>/", views.chatbot_api, name="chatbot_api")
    
    
]
