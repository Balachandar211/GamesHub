from django.db import models
from Store.models import Game
from django.contrib.auth import get_user_model
AppUser = get_user_model()

class GameInteraction(models.Model):
    user           = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    game           = models.ForeignKey(Game, on_delete=models.CASCADE)
    purchase_date  = models.DateTimeField(auto_now_add=True)
    purchase_price = models.FloatField(default=0)
    transaction_id = models.BigAutoField(primary_key=True)
    in_library     = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'game') 

    def get_transaction_id(self):
        return self.transaction_id

    def __str__(self):
        return f"{self.user} bought {self.game}"

class Review(models.Model):
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
    rating         = models.PositiveSmallIntegerField(choices=RATING_CHOICES) 
    upvote         = models.PositiveBigIntegerField(default=0, editable=False)
    downvote       = models.PositiveBigIntegerField(default=0, editable=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'game') 

    def __str__(self):
        return f"{self.user} review for {self.game}"