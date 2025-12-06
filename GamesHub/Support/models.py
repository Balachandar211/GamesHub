from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from Store.models import Game
from django.contrib.auth import get_user_model
User = get_user_model()


class Report(models.Model):
    STATUS     = [
        (1, 'Open'),
        (2, 'Pending'),
        (3, 'Closed'),
        (4, 'Resolved')
    ]
    user          = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_constraint=False)
    body          = models.TextField(null=False, max_length=4096)
    content_type  = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id     = models.PositiveIntegerField()
    parent_object = GenericForeignKey("content_type", "object_id")
    created_at    = models.DateTimeField(auto_now_add=True)
    status        = models.PositiveSmallIntegerField(default= 0, choices=STATUS, null=True, blank=True)

    def __str__(self):
        return f"Report by {self.user.get_username()}"


class Ticket(models.Model):
    ISSUE_TYPE = [
        (1, 'Refund'),
        (2, 'Executable_Issue')
        ]
    
    STATUS     = [
        (1, 'Open'),
        (2, 'Pending'),
        (3, 'Closed'),
        (4, 'Resolved')
    ]
    user          = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_constraint=False)
    game          = models.ForeignKey(Game, on_delete=models.DO_NOTHING, db_constraint=False, null=True, blank=True, default='')
    issue_type    = models.PositiveSmallIntegerField(default= 0, choices=ISSUE_TYPE, null=True, blank=True)
    status        = models.PositiveSmallIntegerField(default= 0, choices=STATUS, null=True, blank=True)
    description   = models.TextField(max_length=4096, null=False)
    evidence      = models.URLField(null=True, default=None, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket by {self.user.get_username()}"

