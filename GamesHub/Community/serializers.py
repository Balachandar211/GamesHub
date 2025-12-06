from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField
from .models import Post, Comment
from rest_framework import serializers
import re
from utills.microservices import validate_vote_value, update_voting_field
from django.contrib.contenttypes.models import ContentType

POST_CONTENT_TYPE    = ContentType.objects.get_for_model(Post)
COMMENT_CONTENT_TYPE = ContentType.objects.get_for_model(Comment)

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

    class Meta:
        model            = Post
        fields           = ["id", "title", "body", "created_at", "user", "hashtags", "comments", "upvote", "downvote"]
        read_only_fields = ["user"]

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

class PostDetailSerializer(PostSerializer):
    upvote_post  = serializers.CharField(write_only=True, required=False)
    downvote_post = serializers.CharField(write_only=True, required=False)

    class Meta:
        model            = Post
        fields           = ["title", "body", "upvote", "downvote", "upvote_post", "downvote_post"]

    def validate(self, attrs):
        if validate_vote_value(attrs, "post"):
            raise ValidationError("Only one of upvote_post or downvote_post can be set.")

        return attrs

    def update(self, instance, validated_data):
        request_user = self.context.get('request_user')
        instance = update_voting_field(instance, validated_data, POST_CONTENT_TYPE, "post", request_user)

        return super().update(instance, validated_data)

class CommentDetailSerializer(CommentSerializer):
    upvote_comment   = serializers.CharField(write_only=True, required=False)
    downvote_comment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model            = Comment
        fields           = ["body", "upvote", "downvote", "upvote_comment", "downvote_comment"]
    
    def update(self, instance, validated_data):
        request_user = self.context.get('request_user')
        instance = update_voting_field(instance, validated_data, COMMENT_CONTENT_TYPE, "comment", request_user)

        return super().update(instance, validated_data)
    
    def validate(self, attrs):
        if validate_vote_value(attrs, "comment"):
            raise ValidationError("Only one of upvote_post or downvote_post can be set.")

        return attrs
