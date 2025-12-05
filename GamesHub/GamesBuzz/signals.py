from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import GameInteraction
from Store.models import Game
from Store.models import GamesMedia
from utills.microservices import delete_cache_key

@receiver(pre_save, sender=GameInteraction)
def update_rating_change(sender, instance, **kwargs):
    try:
        current_instance = sender.objects.get(id=instance.id)
        if current_instance.rating != 0 and current_instance.rating is not None:
            gameObj = Game.objects.get(id = current_instance.game.get_id())
            rating, no_of_rating = gameObj.get_rating_detail()
            current_rating = rating * no_of_rating
            no_of_rating  -= 1
            if no_of_rating != 0:
                new_rating = round((current_rating - current_instance.rating)/no_of_rating, 2)
            else:
                new_rating = 0
            gameObj.set_rating_detail(new_rating, no_of_rating)
            gameObj.save()
    except:
        pass

@receiver(post_save, sender=GameInteraction)
def update_game_rating(sender, instance, **kwargs):
    if instance.rating != 0 and instance.rating is not None:
        gameObj = Game.objects.get(id = instance.game.get_id())
        rating, no_of_rating = gameObj.get_rating_detail()
        current_rating = rating * no_of_rating
        no_of_rating  += 1
        new_rating     = round((current_rating + instance.rating)/no_of_rating, 2)
        gameObj.set_rating_detail(new_rating, no_of_rating)
        gameObj.save()
        delete_cache_key("game")
    delete_cache_key("library")


@receiver(post_save, sender=GamesMedia)
@receiver(post_delete, sender=GamesMedia)
@receiver(post_save, sender=Game)
@receiver(post_delete, sender=Game)
def update_cache(sender, instance, **kwargs):
    delete_cache_key("game")


@receiver(post_delete, sender=GameInteraction)
def update_cache(sender, instance, **kwargs):
    delete_cache_key("library")