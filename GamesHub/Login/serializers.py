from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework import serializers
from utills.storage_supabase import upload_file_to_supabase
from rest_framework.exceptions import ValidationError
import re
from utills.storage_supabase import supabase
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

    def validate_username(self, username):
        if bool(re.match(r"^[A-Za-z0-9@!$]+$", username)):
            return username
        raise ValidationError("Only letters, numbers, and the special characters @, !, and $ are allowed. Spaces and other special characters are not permitted.")

    
    def validate_password(self, rawPassword):
        if bool(re.match(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$", rawPassword)):
            return make_password(rawPassword)
        raise ValidationError("Your password needs at least 8 characters, including an uppercase letter, a number, and a special character.")

    def validate_profilePicture(self, profilePicture):
        valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        max_size = 1024 * 1024
        if profilePicture and profilePicture.size > max_size:
            raise ValidationError("profile picture file size must not exceed 1 MB.")
        if profilePicture and profilePicture.content_type not in valid_mime_types:
            raise ValidationError("Only image files (JPEG, PNG, GIF, WEBP, JPG) are allowed.")
        if profilePicture:
            public_url = upload_file_to_supabase(profilePicture, "ProfilePicture")
            return public_url
        return None
    
   
    def validate_phoneNumber(self, value):
        if value:
            value = re.sub(r'\D', '', value) if not value.startswith('+') else value

            if not value.startswith('+91'):
                value = '+91' + re.sub(r'\D', '', value)

            pattern = r'^\+91\d{10}$'
            if not re.match(pattern, value):
                raise ValidationError("Phone number must start with +91 and contain exactly 10 digits after +91.")

        return value
    

class UserDisplaySerializer(ModelSerializer):
    profilePicture = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profilePicture', 'email', 'phoneNumber']
            
    def get_profilePicture(self, obj):
        if obj.profilePicture is not None:
            profilePicture_path = obj.profilePicture.split("GamesHubMedia/")[1]
            result = supabase.storage.from_("GamesHubMedia").create_signed_url(profilePicture_path, 60)
            return result["signedURL"]
        return None