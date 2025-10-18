from django.db import models

# Create your models here.

class Game(models.Model):
    name          = models.CharField(max_length=256)
    publishedDate = models.DateField()
    description   = models.CharField(max_length=4096)
    price         = models.FloatField(default=0)
    developer     = models.CharField(max_length=256)
    platforms     = models.CharField(max_length=256)
    genre         = models.CharField(max_length=256)

    def __str__(self):
        return self.name
