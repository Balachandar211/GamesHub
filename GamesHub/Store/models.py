from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.validators import MinValueValidator, MaxValueValidator
from utills.storage_supabase import supabase

# Create your models here.

class Game(models.Model):
    name          = models.CharField(max_length=256)
    publishedDate = models.DateField()
    description   = models.CharField(max_length=4096)
    price         = models.FloatField(default=0)
    developer     = models.CharField(max_length=256)
    platforms     = models.CharField(max_length=256)
    genre         = models.CharField(max_length=256)
    discount      = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(100)])
    rating        = models.FloatField(default=0)
    no_of_rating  = models.FloatField(default=0)
    cover_picture = models.URLField(null=True, default=None, blank=True)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def __str__(self):
        return self.name
    
    def get_discount(self):
        return self.discount
    
    def get_actual_price(self):
        return round(((self.price - (self.price * (self.discount)/100))), 2)

    def get_price(self):
        return round(((self.price - (self.price * (self.discount)/100)) + (self.price - (self.price * (self.discount)/100))*0.18), 2)
    
    def get_rating_detail(self):
        return self.rating, self.no_of_rating
    
    def set_rating_detail(self, rating, no_of_rating):
        self.rating       = rating
        self.no_of_rating = no_of_rating

    def get_cover_picture(self):
        if self.cover_picture is not None:
            try:
                cover_picture_path = self.cover_picture.split("GamesHubMedia/")[1]
                result = supabase.storage.from_("GamesHubMedia").create_signed_url(cover_picture_path, 600)
                return result["signedURL"]
            except Exception as e:
                return None
        return None

class GamesMedia(models.Model):
    MEDIA_CHOICES = [
        (0, ''),
        (1, 'Screen_Shot'),
        (2, 'Trailer')
        ]
    game           = models.ForeignKey(Game, on_delete=models.CASCADE)
    media_type     = models.PositiveSmallIntegerField(default= 0, choices=MEDIA_CHOICES, null=True, blank=True) 
    url            = models.URLField(null=True, default=None, blank=True)

class Cart(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    games         = models.ManyToManyField(Game)

class Wishlist(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    games         = models.ManyToManyField(Game)

