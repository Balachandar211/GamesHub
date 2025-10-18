from django.contrib import admin

# Register your models here.
from .models import AppUser, OTP

admin.site.register(AppUser)
admin.site.register(OTP)