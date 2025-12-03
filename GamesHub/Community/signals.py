from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment, Post
from django.core.cache import cache

@receiver(post_save, sender=Post)
@receiver(post_save, sender=Comment)
def update_cache_after_save(sender, instance, **kwargs):
    cache.clear()

@receiver(post_delete, sender=Comment)
@receiver(post_delete, sender=Post)
def update_cache_after_delete(sender, instance, **kwargs):
    cache.clear()