from django.contrib import admin
from django.urls import path
from . import views

app_name="dokumanlar"

urlpatterns = [
    path('dokumanAdd/',views.dokumanAdd,name='dokumanAdd'),
    path('dokumanList/',views.dokumanList,name='dokumanList'),
    path('dokumanUpdate/<int:id>',views.dokumanUpdate,name='dokumanUpdate'),
    path('dokumanSil/<int:id>',views.dokumanSil,name='dokumanSil'),
    path('dokumanView/<int:id>', views.dokumanView, name='dokumanView'),
]