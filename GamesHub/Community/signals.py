from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import PostMedia
from utills.storage_supabase import delete_from_supabase
from django.db import transaction


@receiver(post_delete, sender=PostMedia)
def delete_post_media(sender, instance, **kwargs):
    def _delete():
        if instance.url:
            object_key = instance.url.split("GamesHubMedia/")[-1]
            delete_from_supabase(object_key)

    transaction.on_commit(_delete)
