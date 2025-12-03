from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField
from .models import Post, Comment
from rest_framework import serializers
import re

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

    def update(self, instance, validated_data):
        if validated_data.get("upvote") in ['1', 1, True, "true"]:
            instance.upvote += 1
        if validated_data.get("downvote") in ['1', 1, True, "true"]:
            instance.downvote += 1
        
        return super().update(instance, validated_data)

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

    def update(self, instance, validated_data):
        if validated_data.get("upvote_post") in ['1', 1, True, "true"]:
            instance.upvote += 1
        if validated_data.get("downvote_post") in ['1', 1, True, "true"]:
            instance.downvote += 1

        return super().update(instance, validated_data)

class CommentDetailSerializer(CommentSerializer):
    upvote_comment   = serializers.CharField(write_only=True, required=False)
    downvote_comment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model            = Comment
        fields           = ["body", "upvote", "downvote", "upvote_comment", "downvote_comment"]
    
    def update(self, instance, validated_data):
        if validated_data.get("upvote_comment") in ['1', 1, True, "true"]:
            instance.upvote += 1
        if validated_data.get("downvote_comment") in ['1', 1, True, "true"]:
            instance.downvote += 1

        return super().update(instance, validated_data)
