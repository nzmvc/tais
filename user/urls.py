from django.contrib import admin
from django.urls import path,re_path
from . import views
from django.contrib.auth import views as auth_views #import this

from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)


app_name="user"

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('simpleLogin/<str:userName>/<str:otp>', views.simpleLogin, name='simpleLogin'),
    path('userConfirm/<str:userName>/<str:otp>', views.userConfirm, name='userConfirm'),
    path('reSendActivation/<str:phone>/<str:email>', views.reSendActivation, name='reSendActivation'),
    path('logout/', views.logoutPage, name='logout'),
    path('userAdd/', views.userAdd, name='userAdd'),
    path('userList/<str:ap>', views.userList, name='userList'),
    path('userView/<int:id>', views.userView, name='userView'),
    path('userUpdate/<int:id>', views.userUpdate, name='userUpdate'),
    path('updateMyProfile/', views.updateMyProfile, name='updateMyProfile'),
    path('ChangeMyPassword/', views.ChangeMyPassword, name='ChangeMyPassword'),
    path('userDelete/<int:id>', views.userDelete, name='userDelete'),
    path('userYetki/<int:id>/<str:islem>/<str:perm>',views.userYetki,name ='userYetki'),
    path('userSetAdmin/<int:id>/<str:isAdmin>', views.userSetAdmin, name='userSetAdmin'),
    path('userChangePassword/<int:id>', views.userChangePassword, name='userChangePassword'),
    path('logView/', views.logView, name='logView'),
    path('logViewText/', views.logViewText, name='logViewText'),
    path('logViewSms/', views.logViewSms, name='logViewSms'),
    path('yetkiYok/', views.yetkiYok, name='yetkiYok'),

    path('register/', views.register, name='register'),
    path('simpleRegister/', views.simpleRegister, name='simpleRegister'),
    path('taskmanagerRegister/', views.taskmanagerRegister, name='taskmanagerRegister'),
    path('telephoneConfirm/<str:userid>',views.telephoneConfirm,name='telephoneConfirm'),
    path('passwordResetWithPhone/', views.passwordResetWithPhone, name='passwordResetWithPhone'),
    path('passwordResetWithPhoneConfirm/<str:userid>', views.passwordResetWithPhoneConfirm, name='passwordResetWithPhoneConfirm'),
    path('accountRegister/', views.accountRegister, name='accountRegister'),

    path('departmentAdd/',views.departmentAdd ,name='departmentAdd'),
    path('departmentList/',views.departmentList,name='departmentList'),
    path('departmentDelete/<int:id>/', views.departmentDelete, name='departmentDelete'),
    path('departmentUpdate/<int:id>',views.departmentUpdate, name='departmentUpdate'),
    path('moduleDocs/',views.moduleDocs,name='moduleDocs'),

]
