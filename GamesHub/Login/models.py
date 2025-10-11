from django.db import models
import time
from django.contrib.auth.hashers import make_password

# Create your models here.

class User(models.Model):
    userName       = models.CharField(max_length = 128)
    firstName      = models.CharField(max_length = 128, default="FirstName")
    lastName       = models.CharField(max_length = 128, default="LastName")
    passWord       = models.CharField(max_length = 256)
    profilePicture = models.FileField(upload_to='Media/ProfilePicture/', blank=True, null=True)
    email          = models.EmailField()
    phoneNumber    = models.CharField()
    userType       = models.IntegerField(default=0)

    def get_passWord(self):
        return self.passWord

    def get_userName(self):
        return self.userName
    
    def get_email(self):
        return self.email

    def set_password(self, password):
        self.passWord = make_password(password)

    
class OTP(models.Model):
    otp     = models.IntegerField()
    account = models.CharField(max_length=128)
    time    = models.IntegerField(default=time.time())

    def get_details(self):
        return self.otp, self.time

    def set_details(self, otp, time):
        self.otp, self.time = otp, time
    
    def __str__(self):
        return f"OTP {self.otp} for account {self.account} generated!"
