from .models import Game, Cart, Wishlist
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from utills.storage_supabase import upload_file_to_supabase
from rest_framework.exceptions import ValidationError
import re

class gamesSerializer(ModelSerializer):
    cover_picture     = serializers.ImageField(write_only=True, allow_null=True, required=False, default=None)
    publishedDate     = serializers.DateField(format="%d/%m/%Y")
    cover_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = '__all__'
    
    def validate_cover_picture(self, cover_picture):
        name = self.initial_data.get("name")

        if not name and hasattr(self, "instance"):
            name = getattr(self.instance, "name")

        
        safe_path = re.sub(r'[^a-zA-Z0-9\-_/\.]', '', name)

        valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if cover_picture and cover_picture.content_type not in valid_mime_types:
            raise ValidationError("Only image files (JPEG, PNG, GIF, WEBP, JPG) are allowed.")
        if cover_picture:
            public_url = upload_file_to_supabase(cover_picture, f"{safe_path}/cover_picture")
            return public_url
        return None
    
    def get_cover_picture_url(self, obj):
        return obj.get_cover_picture()

class gamesSerializerSimplified(ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model  = Game
        fields = ('id', 'name', 'developer', 'price')
    
    def get_price(self, obj):
        return obj.get_actual_price()

class cartSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    games = gamesSerializerSimplified(many=True)

    class Meta:
        model = Cart
        fields = ['user', 'games']

    def get_user(self, obj):
        return obj.user.get_username()

    
class wishlistSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    games = gamesSerializerSimplified(many=True)

    class Meta:
        model = Wishlist
        fields = ['user', 'games']

    def get_user(self, obj):
        return obj.user.get_username()
