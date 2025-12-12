from django.contrib import admin
from .models import Report, Ticket, BanUser

admin.site.register(Report)
admin.site.register(Ticket)
admin.site.register(BanUser)
