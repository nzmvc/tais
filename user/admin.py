from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Logging,Departments,Sube,Yetenek,Yetki,Yetkilendirme
from user.models import Employee

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'employee'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Employee)
admin.site.register(Logging)
admin.site.register(Departments)
admin.site.register(Sube)
admin.site.register(Yetenek)
admin.site.register(Yetki)
admin.site.register(Yetkilendirme)
