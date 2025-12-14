from django.db import models
import re
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from utills.storage_supabase import supabase
User = get_user_model()


class HashTags(models.Model):
    tag           = models.CharField(max_length=32)

    def __str__(self):
        return self.tag

class Post(models.Model):
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title         = models.CharField(max_length=256, null=False, blank=False)
    body          = models.TextField(max_length=4096, null=False, blank=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    hashtags      = models.ManyToManyField(HashTags, editable=False, related_name="hastags")
    comments      = GenericRelation("Comment", related_query_name="post")
    upvote        = models.PositiveBigIntegerField(default=0, editable=False)
    downvote      = models.PositiveBigIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        pattern  = re.compile(r'#\w{1,31}', re.MULTILINE)
        matches  = pattern.findall(self.body)
        hashtags = []

        for match in matches:
            hashtag, _ = HashTags.objects.get_or_create(tag=match.strip().lower())
            hashtags.append(hashtag)

        self.hashtags.set(hashtags)

        return self


    def __str__(self):
        if self.user is not None:
            user = self.user.get_username()
        else:
            user = "Deleted User"
        return self.title + " by " + user


class Comment(models.Model):
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body          = models.TextField(null=False, max_length=4096)
    content_type  = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id     = models.PositiveIntegerField()
    parent_object = GenericForeignKey("content_type", "object_id")
    created_at    = models.DateTimeField(auto_now_add=True)
    upvote        = models.PositiveBigIntegerField(default=0, editable=False)
    downvote      = models.PositiveBigIntegerField(default=0, editable=False)


    def __str__(self):
        return f"Comment for {self.parent_object.title}"

class PostMedia(models.Model):
    post           = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    url            = models.URLField(null=True, default=None, blank=True)

    def get_url(self):
        media  = self.url.split("GamesHubMedia/")[1]
        result = supabase.storage.from_("GamesHubMedia").create_signed_url(media, 600)
        return result["signedURL"]

    def __str__(self):
        return f"media for {self.post}"