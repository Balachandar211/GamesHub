from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework import serializers
from utills.storage_supabase import upload_file_to_supabase
from rest_framework.exceptions import ValidationError
User = get_user_model()

class userSerializer(ModelSerializer):
    profilePicture = serializers.ImageField(write_only=True, allow_null=True, required=False, default=None)
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'default': True}
        }

    
    def validate_password(self, rawPassword):
        return make_password(rawPassword)

    def validate_profilePicture(self, profilePicture):
        valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if profilePicture and profilePicture.content_type not in valid_mime_types:
            raise ValidationError("Only image files (JPEG, PNG, GIF, WEBP, JPG) are allowed.")
        if profilePicture:
            public_url = upload_file_to_supabase(profilePicture, "ProfilePicture")
            return public_url
        return None