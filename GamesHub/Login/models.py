from django.db import models
from django.contrib.auth.models import AbstractUser
from utills.storage_supabase import supabase
from django.utils import timezone

class AppUser(AbstractUser):
    profilePicture = models.URLField(null=True, default=None, blank=True)
    email          = models.EmailField()
    phoneNumber    = models.CharField(max_length=15, null=True, default=None, blank=True)
    is_active      = models.BooleanField(default=True)  
    valid_email    = models.BooleanField(default=False)  


    def get_email(self):
        return self.email
    
    def get_profilePicture(self):
        if self.profilePicture is not None:
            profilePicture_path = self.profilePicture.split("GamesHubMedia/")[1]
            result = supabase.storage.from_("GamesHubMedia").create_signed_url(profilePicture_path, 60)
            return result["signedURL"]
        return None
    
    def get_profilePicture_url(self):
        return self.profilePicture

    def get_password(self):
        return self.password
    
    def change_status(self):
        self.is_active = not self.is_active

    def set_last_login(self):
        self.last_login = timezone.now()

    def set_valid_email(self):
        self.valid_email = True
    
    def __str__(self):
        return self.username

    
class OTP(models.Model):
    otp     = models.IntegerField(null=True, default=None, blank=True)
    account = models.CharField(max_length=128)
    time    = models.IntegerField(null=True, default=None, blank=True)

    def get_details(self):
        return self.otp, self.time

    def set_details(self, otp, time):
        self.otp, self.time = otp, time
    
    def __str__(self):
        return f"OTP {self.otp} for account {self.account} generated!"
