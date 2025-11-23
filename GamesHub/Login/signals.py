from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from utills.storage_supabase import delete_from_supabase
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_delete, sender=User)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profilePicture:
        object_key = instance.profilePicture.split("GamesHubMedia/")[-1]
        delete_from_supabase(object_key)
