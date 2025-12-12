from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField
from .models import Post, Comment, PostMedia
from rest_framework import serializers
import re
from utills.microservices import validate_vote_value, update_voting_field
from django.contrib.contenttypes.models import ContentType
from utills.storage_supabase import upload_file_to_supabase, supabase
from django.db import transaction

POST_CONTENT_TYPE    = ContentType.objects.get_for_model(Post)
COMMENT_CONTENT_TYPE = ContentType.objects.get_for_model(Comment)

def get_signed_url(path):
    return supabase.storage.from_("GamesHubMedia").create_signed_url(path, 3600)["signedURL"]

class CommentSerializer(ModelSerializer):

    class Meta:
        model            = Comment
        fields           = '__all__'
        read_only_fields = ["user", "parent_object", "object_id", "content_type"]

    
    def validate_body(self, value):
        for pattern in [re.compile(r"(?i)\bass\b"), re.compile(r"(?i)\bfuck\b"), re.compile(r"(?i)\bbitch\b"), re.compile(r"(?i)\basshole\b"),]:
            if pattern.search(value):
                raise ValidationError("body cannot have banned words")
        
        return value

class PostSerializer(ModelSerializer):
    comments  = SerializerMethodField()
    media     = serializers.ListField(child = serializers.FileField(), write_only = True, required=False, allow_empty=True)
    media_url = SerializerMethodField(read_only = True)
    username  = SerializerMethodField(read_only = True) 

    class Meta:
        model            = Post
        fields           = ["id", "title", "body", "created_at", "user", "username", "hashtags", "comments", "upvote", "downvote", "media", "media_url"]
        read_only_fields = ["user"]

    def validate_media(self, media):
        if len(media) > 3:
            raise ValidationError("Only three media files can be uploaded.")
        
        valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4"]

        max_size_post  = 1024 * 1024
        max_size_video = 10 * 1024 * 1024

        for f in media:
            
            if f.content_type not in valid_mime_types:
                raise ValidationError("Only image files (JPEG, PNG, GIF, WEBP, JPG, MP4) are allowed.")
            
            if f.size > max_size_video and f.content_type == "video/mp4":
                raise ValidationError("video file size must not exceed 10 MB.")
            elif f.size > max_size_post and f.content_type != "video/mp4":
                raise ValidationError("image file size must not exceed 1 MB.")

        return media

    @transaction.atomic
    def create(self, validated_data):
        files  = validated_data.pop("media", [])
        post = Post.objects.create(**validated_data)

        for f in files:            
            url = upload_file_to_supabase(f, f"Posts/{post.id}/Media")
            PostMedia.objects.create(post=post, url=url)

        return post

    def validate_title(self, value):
        for pattern in [re.compile(r"(?i)\bass\b"), re.compile(r"(?i)\bfuck\b"), re.compile(r"(?i)\bbitch\b"), re.compile(r"(?i)\basshole\b"),]:
            if pattern.search(value):
                raise ValidationError("title cannot have banned words")
        
        return value

    def validate_body(self, value):
        for pattern in [re.compile(r"(?i)\bass\b"), re.compile(r"(?i)\bfuck\b"), re.compile(r"(?i)\bbitch\b"), re.compile(r"(?i)\basshole\b"),]:
            if pattern.search(value):
                raise ValidationError("body cannot have banned words")
        
        return value
    
    def get_comments(self, obj):
        comments = obj.comments.order_by("-created_at")[:5]
        return CommentSerializer(comments, many=True).data

    def get_media_url(self, obj):
        media_objs = obj.media.all()
        paths = [m.get_url() for m in media_objs if m.url]

        return paths
    
    def get_username(self, obj):
        return obj.user.get_username()


class PostDetailSerializer(PostSerializer):
    upvote_post   = serializers.CharField(write_only=True, required=False)
    downvote_post = serializers.CharField(write_only=True, required=False)
    media_url     = SerializerMethodField(read_only = True)

    class Meta:
        model            = Post
        fields           = ["title", "body", "upvote", "downvote", "upvote_post", "downvote_post", "media_url", "media"]

    def validate(self, attrs):
        if validate_vote_value(attrs, "post"):
            raise ValidationError("Only one of upvote_post or downvote_post can be set.")

        return attrs

        
    @transaction.atomic
    def update(self, instance, validated_data):
        media = validated_data.pop("media", None)

        if media is not None:
            PostMedia.objects.filter(post=instance).delete()

            for f in media:
                url = upload_file_to_supabase(f, f"Posts/{instance.id}/Media")
                PostMedia.objects.create(post=instance, url=url)     

        request_user = self.context.get('request_user')
        model_obj    = Post.objects.filter(id = instance.id)
        instance = update_voting_field(instance, validated_data, POST_CONTENT_TYPE, "post", request_user, model_obj)

        return super().update(instance, validated_data)
    
    def get_media_url(self, obj):
        media_objs = obj.media.all()
        paths = [m.get_url() for m in media_objs if m.url]

        return paths

class CommentDetailSerializer(CommentSerializer):
    upvote_comment   = serializers.CharField(write_only=True, required=False)
    downvote_comment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model            = Comment
        fields           = ["body", "upvote", "downvote", "upvote_comment", "downvote_comment"]
    
    def update(self, instance, validated_data):
        request_user = self.context.get('request_user')
        model_obj    = Comment.objects.filter(id = instance.id)
        instance = update_voting_field(instance, validated_data, COMMENT_CONTENT_TYPE, "comment", request_user, model_obj)

        return super().update(instance, validated_data)
    
    def validate(self, attrs):
        if validate_vote_value(attrs, "comment"):
            raise ValidationError("Only one of upvote_comment or downvote_comment can be set.")

        return attrs
