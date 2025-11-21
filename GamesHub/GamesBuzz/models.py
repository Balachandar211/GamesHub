from django.db import models
from Store.models import Game
from django.contrib.auth import get_user_model
AppUser = get_user_model()

class GameInteraction(models.Model):
    RATING_CHOICES = [
        (0, '.....'),
        (1, '*....'),
        (2, '**...'),
        (3, '***..'),
        (4, '****.'),
        (5, '*****'),
        ]
    user           = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    game           = models.ForeignKey(Game, on_delete=models.CASCADE)
    comment        = models.TextField(blank=True)
    rating         = models.PositiveSmallIntegerField(default= 0, choices=RATING_CHOICES, null=True, blank=True) 
    purchase_date  = models.DateTimeField(auto_now_add=True)
    purchase_price = models.FloatField(default=0)
    transaction_id = models.IntegerField(default=0)
    in_library     = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'game') 

    def __str__(self):
        return f"{self.user} bought {self.game}"
    
