from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Constants(models.Model):
    variable   = models.CharField(max_length=32)
    value      = models.CharField(max_length=64)

    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

    def __str__(self):
        return self.variable
    
class BlacklistedAccessToken(models.Model):
    access_token         = models.CharField(max_length=1024)
    blacklisted_time     = models.DateTimeField()
