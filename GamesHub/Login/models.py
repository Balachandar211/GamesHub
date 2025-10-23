from django.db import models
import time
from django.contrib.auth.models import AbstractUser
import base64


class AppUser(AbstractUser):
    profilePicture = models.FileField(upload_to='Media/ProfilePicture/', blank=True, null=True)
    email          = models.EmailField()
    phoneNumber    = models.CharField()
    is_active      = models.BooleanField(default=True)  

    def get_email(self):
        return self.email
    
    def get_profilePicture(self):
        if not (self.profilePicture and hasattr(self.profilePicture, 'url')):
            return None

        with self.profilePicture.open('rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        
        return encoded
    
    def __str__(self):
        return self.username

    
class OTP(models.Model):
    otp     = models.IntegerField()
    account = models.CharField(max_length=128)
    time    = models.IntegerField()

    def get_details(self):
        return self.otp, self.time

    def set_details(self, otp, time):
        self.otp, self.time = otp, time
    
    def __str__(self):
        return f"OTP {self.otp} for account {self.account} generated!"
