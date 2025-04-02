from django.urls import include, path
from rest_framework import routers
from api.views import GorevlerView, GorevlerDeatilView, GorevlerDeleteView, GorevlerUpdateView, GorevlerCreateView,check_activation_status


urlpatterns = [
    path('gorevler', GorevlerView.as_view(),name='gorevler'),
    path('gorevlerDetail/<int:id>', GorevlerDeatilView.as_view(),name='gorevler_detail'),
    path('gorevlerDelete/<int:id>', GorevlerDeleteView.as_view(),name='gorevler_delete'),
    path('gorevlerUpdate/<int:id>', GorevlerUpdateView.as_view(),name='gorevler_update'),
    path('gorevlerCreate', GorevlerCreateView.as_view(),name='gorevler_create'),
    
    path('check-activation-status/', check_activation_status, name='check_activation_status'),
]