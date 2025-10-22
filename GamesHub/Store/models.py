from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.


class Game(models.Model):
    name          = models.CharField(max_length=256)
    publishedDate = models.DateField()
    description   = models.CharField(max_length=4096)
    price         = models.FloatField(default=0)
    developer     = models.CharField(max_length=256)
    platforms     = models.CharField(max_length=256)
    genre         = models.CharField(max_length=256)

    def get_name(self):
        return self.name

    def __str__(self):
        return self.name


class Cart(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    games         = models.ManyToManyField(Game)

class Purchase(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    games         = models.ManyToManyField(Game)

class Library(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    games         = models.ManyToManyField(Game)

