from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from Store.models import Game
from django.utils import timezone
from utills.storage_supabase import supabase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
User = get_user_model()


class Report(models.Model):
    STATUS     = [
        (1, 'Open'),
        (2, 'Pending'),
        (3, 'Closed'),
        (4, 'Resolved')
    ]
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body            = models.TextField(null=False, max_length=4096)
    content_type    = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id       = models.PositiveIntegerField()
    parent_object   = GenericForeignKey("content_type", "object_id")
    created_at      = models.DateTimeField(auto_now_add=True)
    status          = models.PositiveSmallIntegerField(default= 1, choices=STATUS, null=True, blank=True)
    assigned_staff  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_staff_report")
    resolution_date = models.DateTimeField(null=True, blank=True, editable=False)
    admin_comment   = models.TextField(null=True, max_length=4096)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Report.objects.get(pk=self.pk)
            if old.status != self.status and self.status in (3, 4):
                self.resolution_date = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report by {self.user.get_username()} on {self.content_type}"


class Ticket(models.Model):
    ISSUE_TYPE = [
        (1, 'Refund'),
        (2, 'Executable_Issue'),
        (3, 'Other')
        ]
    
    STATUS     = [
        (1, 'Open'),
        (2, 'Pending'),
        (3, 'Closed'),
        (4, 'Resolved')
    ]
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    game            = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    issue_type      = models.PositiveSmallIntegerField(default= 3, choices=ISSUE_TYPE, null=True, blank=True)
    status          = models.PositiveSmallIntegerField(default= 1, choices=STATUS, null=True, blank=True)
    description     = models.TextField(max_length=4096, null=False)
    evidence        = models.URLField(null=True, default=None, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    assigned_staff  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_staff_ticket")
    resolution_date = models.DateTimeField(null=True, blank=True, editable=False)
    admin_comment   = models.TextField(null=True, max_length=4096)
    comments        = GenericRelation("Community.Comment", related_query_name="ticket")

    def get_evidence(self):
        if self.evidence is not None:
            evidence_path = self.evidence.split("GamesHubMedia/")[1]
            result = supabase.storage.from_("GamesHubMedia").create_signed_url(evidence_path, 60)
            return result["signedURL"]
        return None

    def __str__(self):
        return f"Ticket by {self.user.get_username()}"
    

class BanUser(models.Model):
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ban_count     = models.PositiveIntegerField(default=0)
    baned_date    = models.DateField()

    def save(self, *args, **kwargs):
        self.ban_count += 1
        self.baned_date = timezone.now()
        return super().save(*args, **kwargs)
    
    def get_ban_count(self):
        return self.ban_count

    def __str__(self):
        if self.user is not None:
            user = self.user.get_username()
        else:
            user = "Deleted User"
        return f"{user} banned {self.ban_count} times"

