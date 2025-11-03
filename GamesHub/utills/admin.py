from django.contrib import admin
from .models import Constants, BlacklistedAccessToken
# Register your models here.

admin.site.register(Constants)
admin.site.register(BlacklistedAccessToken)