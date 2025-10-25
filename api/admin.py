from django.contrib import admin

# Register your models here.
from api.models import *


admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(KYCDocument)
admin.site.register(AuditLog)
