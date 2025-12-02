from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Post, Comment
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
    comments  = CommentSerializer(many=True, read_only=True)

    class Meta:
        model            = Post
        fields           = ["id", "title", "body", "created_at", "user", "hashtags", "comments"]
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

