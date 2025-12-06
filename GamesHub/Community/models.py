from django.db import models
import re
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
User = get_user_model()


class HashTags(models.Model):
    tag           = models.CharField(max_length=32)

    def __str__(self):
        return self.tag

class Post(models.Model):
    user          = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_constraint=False)
    title         = models.CharField(max_length=256, null=False, blank=False)
    body          = models.TextField(max_length=4096, null=False, blank=False)
    created_at    = models.DateField(auto_now_add=True)
    hashtags      = models.ManyToManyField(HashTags, editable=False)
    comments      = GenericRelation("Comment", related_query_name="post")
    upvote        = models.PositiveBigIntegerField(default=0, editable=False)
    downvote      = models.PositiveBigIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        pattern  = re.compile(r'#\w{1,31}', re.MULTILINE)
        matches  = pattern.findall(self.body)
        hashtags = []

        for match in matches:
            hashtag, _ = HashTags.objects.get_or_create(tag=match)
            hashtags.append(hashtag)

        self.hashtags.set(hashtags)

        return self


    def __str__(self):
        try:
            user = self.user.get_username()
        except User.DoesNotExist:
            user = "Deleted User"
        return self.title + " by " + user


class Comment(models.Model):
    user          = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_constraint=False)
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
    MEDIA_CHOICES = [
        (1, 'Screen_Shot'),
        (2, 'Gameplay')
        ]
    post           = models.ForeignKey(Post, on_delete=models.CASCADE)
    media_type     = models.PositiveSmallIntegerField(default= 0, choices=MEDIA_CHOICES, null=True, blank=True) 
    url            = models.URLField(null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.get_media_type_display()} for {self.game}"