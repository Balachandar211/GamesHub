from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from utills.storage_supabase import supabase
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

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

    class Meta:
        ordering = ["id"]

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
        (1, 'Screen_Shot'),
        (2, 'Trailer')
        ]
    game           = models.ForeignKey(Game, on_delete=models.CASCADE)
    media_type     = models.PositiveSmallIntegerField(default= 0, choices=MEDIA_CHOICES, null=True, blank=True) 
    url            = models.URLField(null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.get_media_type_display()} for {self.game.get_name()}"

class Cart(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    games         = models.ManyToManyField(Game)

    def __str__(self):
        return "cart for user " + self.user.get_username()

class Wishlist(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    games         = models.ManyToManyField(Game)

    def __str__(self):
        return "wishlist for user " + self.user.get_username()
    
class Wallet(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, null=True, blank=True)
    balance       = models.DecimalField(default=Decimal('0.00'), decimal_places=2, max_digits=12)

    def get_balance(self):
        return self.balance

    def __str__(self):
        return f"Wallet for user {self.user.get_username()}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPE = [
        (1, 'credit'),
        (2, 'debit')
        ]
    
    PAYMENT_TYPE = [
        (1, "recharge"),
        (2, "refund"),
        (3, "payment")
    ]

    wallet           = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING, db_constraint=False)
    transaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPE, editable=False)
    amount           = models.DecimalField(default=Decimal('0.00'), decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal('0.00'))])
    created_at       = models.DateTimeField(auto_now_add=True)
    payment_type     = models.PositiveSmallIntegerField(choices=PAYMENT_TYPE)
    transaction_id   = models.BigAutoField(primary_key=True)

    def get_transaction_id(self):
        return self.transaction_id

    def clean(self):
        if self.payment_type == 3 and self.wallet.balance - self.amount < 0:
            raise ValidationError(f"Not enough money in wallet for payment of {self.amount}. Wallet balance is {self.wallet.balance}")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.payment_type in [1, 2]:
                self.wallet.balance += self.amount
                self.transaction_type = 1
            else:
                self.wallet.balance -= self.amount
                self.transaction_type = 2
            
            self.wallet.save()

            return super().save(*args, **kwargs)
    
    def __str__(self):
        try:
            user = self.wallet.user.get_username()
        except Wallet.DoesNotExist:
            user = "Deleted User"
        return f"{self.get_payment_type_display()} for user {user}"
    


class Sale(models.Model):
    sale_name           = models.CharField(max_length=32)
    description         = models.CharField(max_length=2048, default='')
    games               = models.ManyToManyField(Game)
    sale_end_date       = models.DateTimeField(null=True, blank=True)
    cover_picture       = models.URLField(null=False)

    def get_cover_picture(self):
        if self.cover_picture is not None:
            try:
                cover_picture_path = self.cover_picture.split("GamesHubMedia/")[1]
                result = supabase.storage.from_("GamesHubMedia").create_signed_url(cover_picture_path, 600)
                return result["signedURL"]
            except Exception as e:
                return None
        return None

    def __str__(self):
        return self.sale_name