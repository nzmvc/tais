from django.contrib import admin
from django.urls import path
from . import views

app_name="saas"

urlpatterns = [
    path('companyAdd/',views.companyAdd,name='companyAdd'),
    path('companyDelete/<int:id>',views.companyDelete,name='companyDelete'),
    path('companyList/<str:ap>',views.companyList,name='companyList'),
    #path('companyView/<int:id>',views.companyView,name='companyView'),
    path('companyUpdate/<int:id>',views.companyUpdate,name='companyUpdate'),
    path('companyStatu/<int:id>/<str:statu>',views.companyStatu,name='companyStatu'),

    path('myCompanyUpdate',views.myCompanyUpdate,name='myCompanyUpdate'),
]