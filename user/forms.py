from django import forms
from django.contrib.auth.models import User
from .models import Employee


class LoginForm(forms.Form):
    username = forms.CharField(label = "Username")
    password = forms.CharField(label = "Password",widget=forms.PasswordInput)


class AccountRegisterForm(forms.Form):
    first_name = forms.CharField(max_length=20, label="Ad")
    second_name = forms.CharField(max_length=20, label="Soyad")
    telephone = forms.CharField(max_length=50, label="Telefon")
    email = forms.EmailField(max_length=100,label="Email")
    company = forms.CharField(max_length=50, label="Şirket")

    def clean(self):
        first_name  = self.cleaned_data.get("first_name")
        second_name = self.cleaned_data.get("second_name")
        telephone   = self.cleaned_data.get("telephone")
        email       = self.cleaned_data.get("email")
        company     = self.cleaned_data.get("company")

        values = {
            "first_name":first_name,
            "second_name":second_name,
            "telephone":telephone,
            "email":email,
            "company":company
        }
        return values
        
#class RegisterForm(forms.Form):
class RegisterForm(forms.ModelForm):

    #username = forms.CharField(max_length=50, label="Kullanıcı Adı")
    password = forms.CharField(max_length=20,label="Sifre",widget=forms.PasswordInput)
    confirm = forms.CharField(max_length=20,label="Parola doğrula",widget=forms.PasswordInput)
    telephone = forms.CharField(max_length=50, label="Telefon")
    email = forms.EmailField(max_length=100,label="Email")
    #sube = forms.ChoiceField(label="Şube")
    first_name = forms.CharField(max_length=20, label="Ad")
    last_name = forms.CharField(max_length=20, label="Soyad")
    
    #department = forms.ChoiceField(label="Departmant")
    
    def clean(self):
        #username    = self.cleaned_data.get("username")
        password    = self.cleaned_data.get("password")
        first_name  = self.cleaned_data.get("first_name")
        last_name   = self.cleaned_data.get("last_name")
        confirm     = self.cleaned_data.get("confirm")
        telephone   = self.cleaned_data.get("telephone")
        telephone2   = self.cleaned_data.get("telephone2")
        email       = self.cleaned_data.get("email")
        sube        = self.cleaned_data.get("sube")
        department  = self.cleaned_data.get("department")
        isAdmin  = self.cleaned_data.get("isAdmin")
        #yetenek      = self.cleaned_data.get("yetenek")
        #if username and password and password != confirm:
        if password != confirm:
            
            raise forms.ValidationError("parolalar eşleşmiyor")

        values = {
            #"username":username,
            "password":password,
            "telephone":telephone,
            "telephone2":telephone2,
            "email":email,
            "sube":sube,
            "first_name":first_name,
            "last_name":last_name,
            "department":department,
            "isAdmin":isAdmin,
            #"yetenek":yetenek,
        }
        return values

    class Meta:
        model = Employee
        
        fields = ['password','sube','department','yetenek','telephone','telephone2','isAdmin']
        #fields = ['username','password','sube','department','yetenek','telephone']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','first_name','last_name']
        #fields = ['username','email','first_name','last_name','telephone','sube','department','yetenek']


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['profilePhoto', 'telephone','telephone2', 'yetenek', 'about', 'education', 'experience']

class ChangePassword(forms.Form):

    password = forms.CharField(max_length=20,label="Sifre",widget=forms.PasswordInput)
    confirm = forms.CharField(max_length=20,label="Şifre doğrula",widget=forms.PasswordInput)

    def clean(self):
        password    = self.cleaned_data.get("password")
        confirm     = self.cleaned_data.get("confirm")

        if len(password) < 8:
            raise forms.ValidationError("Parola en az 8 karakter olmalı")
        

        if password != confirm:
            
            raise forms.ValidationError("parolalar eşleşmiyor")
        # check for digit
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError('Parola en az 1 sayı içermeli')

        # check for letter
        if not any(char.isalpha() for char in password):
            raise forms.ValidationError('Parola en az 1 harf içermeli')

        values = {
            "password":password,
            "confirm":confirm
        }
        return values

class DepartmentForm(forms.Form):
    title = forms.CharField(max_length=50,label="Departman Adı")

    def clean(self):
        title = self.cleaned_data.get("title")
        if title == "":
            raise forms.ValidationError("Departman adı boş olamaz")
        values = {
            "title":title
        }
        return values