from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Gorevler)
admin.site.register(GorevNotu)
admin.site.register(GorevlerStatu)
admin.site.register(GorevType)
admin.site.register(DuzenliGorevTanim)
