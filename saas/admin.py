from django.contrib import admin
from saas.models import *

admin.site.register(Company)
admin.site.register(Sector)
admin.site.register(Modules)
admin.site.register(CompanyModules)
admin.site.register(CompanyStatus)

