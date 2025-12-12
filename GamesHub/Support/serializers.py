from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField, FileField
from .models import Report, Ticket
import re
from django.contrib.auth import get_user_model
from utills.storage_supabase import supabase, upload_file_to_supabase
from Community.serializers import CommentSerializer
User = get_user_model()


class ReportSerializer(ModelSerializer):

    class Meta:
        model            = Report
        fields           = "__all__"
        read_only_fields = ["user", "parent_object", "object_id", "content_type", "assigned_staff", "resolution_date"]

    def validate_body(self, value):
        for pattern in [re.compile(r"(?i)\bass\b"), re.compile(r"(?i)\bfuck\b"), re.compile(r"(?i)\bbitch\b"), re.compile(r"(?i)\basshole\b"),]:
            if pattern.search(value):
                raise ValidationError("body cannot have banned words")
        
        return value

    def update(self, instance, validated_data):
        assigned_staff = self.context.pop("assigned_staff", None)
        if assigned_staff is not None or instance.assigned_staff is None:
            instance.assigned_staff = assigned_staff
            instance.status         = 2
        return super().update(instance, validated_data)
    
class TicketSerializer(ReportSerializer):
    evidence_url     = SerializerMethodField(read_only = True)
    
    class Meta:
        model            = Ticket
        fields           = "__all__"
        read_only_fields = ["user", "parent_object", "object_id", "content_type"]


    def get_evidence_url(self, obj):
        return obj.get_evidence()

class UserTicketSerializer(TicketSerializer):
    comments      = SerializerMethodField()
    evidence      = FileField(write_only = True, allow_null=True, required=False, default=None)
    class Meta:
        model            = Ticket
        fields           = ["id", "issue_type", "status", "description", "evidence", "evidence_url", "comments"]
        read_only_fields = ["issue_type", "status", "id"]

    def validate_evidence(self, evidence):
        valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"]
        max_size = 1024 * 1024
        if evidence and evidence.size > max_size:  
            raise ValidationError("evidence size must not exceed 1 MB.")
        if evidence and evidence.content_type not in valid_mime_types:
            raise ValidationError("Only following files (JPEG, PNG, GIF, WEBP, JPG, PDF) are allowed.")

        return evidence
    
    def create(self, validated_data):
        evidence = validated_data.pop("evidence", None)

        ticket = super().create(validated_data)

        if evidence:
            folder = f"evidence/{ticket.pk}"
            public_url = upload_file_to_supabase(evidence, folder)
            ticket.evidence = public_url
            ticket.save(update_fields=["evidence"])

        return ticket

    def get_comments(self, obj):
        comments = obj.comments.order_by("created_at")
        return CommentSerializer(comments, many=True).data

class AdminUserDisplaySerializer(ModelSerializer):
    profilePicture = SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profilePicture', 'email', 'phoneNumber']
            
    def get_profilePicture(self, obj):
        if obj.profilePicture is not None:
            profilePicture_path = obj.profilePicture.split("GamesHubMedia/")[1]
            result = supabase.storage.from_("GamesHubMedia").create_signed_url(profilePicture_path, 60)
            return result["signedURL"]
        return None


class UserTicketResolveSerializer(ModelSerializer):
    comments      = SerializerMethodField()
    evidence_url     = SerializerMethodField(read_only = True)
    class Meta:
        model            = Ticket
        fields           = ["assigned_staff", "issue_type", "status", "description", "created_at", "admin_comment", "evidence_url", "comments"]
        read_only_fields = ["issue_type", "description", "created_at", "assigned_staff"]

    
    def update(self, instance, validated_data):
        assigned_staff = self.context.pop("assigned_staff", None)
        if assigned_staff is not None or instance.assigned_staff is None:
            print(assigned_staff)
            instance.assigned_staff = assigned_staff
            instance.status         = 2
        return super().update(instance, validated_data)
    
    
    def get_evidence_url(self, obj):
        return obj.get_evidence()
    
    def get_comments(self, obj):
        comments = obj.comments.order_by("created_at")
        return CommentSerializer(comments, many=True).data