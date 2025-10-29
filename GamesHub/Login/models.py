from django.db import models
from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    profilePicture = models.CharField(null=True, default=None, blank=True)
    email          = models.EmailField()
    phoneNumber    = models.CharField(max_length=15, null=True, default=None)
    is_active      = models.BooleanField(default=True)  

    def get_email(self):
        return self.email
    
    def get_profilePicture(self):
        return self.profilePicture
    
    def get_password(self):
        return self.password
    
    def change_status(self):
        self.is_active = not self.is_active
    
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
