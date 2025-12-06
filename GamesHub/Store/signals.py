from django.db.models.signals import post_delete,  pre_save
from django.dispatch import receiver
from .models import Sale, Game
from utills.storage_supabase import delete_from_supabase


@receiver(post_delete, sender=Game)
@receiver(post_delete, sender=Sale)
def delete_cover_picture(sender, instance, **kwargs):
    if instance.cover_picture:
        object_key = instance.cover_picture.split("GamesHubMedia/")[-1]
        delete_from_supabase(object_key)


@receiver(pre_save, sender=Game)
@receiver(pre_save, sender=Sale)
def delete_old_cover_picture(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    if old_instance.cover_picture and old_instance.cover_picture != instance.cover_picture:
        object_key = old_instance.cover_picture.split("GamesHubMedia/")[-1]
        delete_from_supabase(object_key)
