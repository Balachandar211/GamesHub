from django.contrib import admin
from .models import Constants, BlacklistedAccessToken, UpvoteDownvoteControl
# Register your models here.

admin.site.register(Constants)
admin.site.register(BlacklistedAccessToken)
admin.site.register(UpvoteDownvoteControl)