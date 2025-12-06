from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()

class Constants(models.Model):
    variable   = models.CharField(max_length=32)
    value      = models.CharField(max_length=64)

    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

    def __str__(self):
        return self.variable
    
class BlacklistedAccessToken(models.Model):
    access_token         = models.CharField(max_length=1024)
    blacklisted_time     = models.DateTimeField()

class UpvoteDownvoteControl(models.Model):
    user           = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_constraint=False)
    content_type   = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id      = models.PositiveIntegerField()
    parent_object  = GenericForeignKey("content_type", "object_id")
    upvotedownvote = models.BooleanField(default=None, null=True, blank=True)

    def get_vote_type(self):
        return self.upvotedownvote
    
    def set_vote_type(self, upvotedownvote):
        self.upvotedownvote = upvotedownvote

    def __str__(self):
        return f"Upvote downvote control for {self.content_type} by {self.user.get_username()} on object id {self.object_id}"

