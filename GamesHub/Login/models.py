from django.db import models

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