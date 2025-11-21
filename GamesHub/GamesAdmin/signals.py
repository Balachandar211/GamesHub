from django.db.models.signals import post_delete
from django.dispatch import receiver
from utills.storage_supabase import delete_from_supabase
from Store.models import GamesMedia

@receiver(post_delete, sender=GamesMedia)
def delete_screen_shot(sender, instance, **kwargs):
    if instance.media_type == 1:
        object_key = instance.url.split("GamesHubMedia/")[-1]
        delete_from_supabase(object_key)
