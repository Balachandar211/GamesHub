from .models import Game, Cart, Wishlist, GamesMedia, Wallet, WalletTransaction, Sale
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from utills.storage_supabase import upload_file_to_supabase
from rest_framework.exceptions import ValidationError
from utills.storage_supabase import supabase
from utills.game_media_update import get_cover_url
from datetime import timedelta
from django.utils import timezone
import json
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

        if cover_picture:
            valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if cover_picture.content_type not in valid_mime_types:
                raise ValidationError("Only image files (JPEG, PNG, GIF, WEBP, JPG) are allowed.")
        else:
            cover_picture = get_cover_url(name)
            
        if cover_picture:
            if not name and hasattr(self, "instance"):
                name = getattr(self.instance, "name")

            safe_path = re.sub(r'[^a-zA-Z0-9\-_/\.]', '', name)
            
            public_url = upload_file_to_supabase(cover_picture, f"{safe_path}/cover_picture")
            return public_url

        return None
    
    def get_cover_picture_url(self, obj):
        return obj.get_cover_picture()

class gamesSerializerSimplified(ModelSerializer):
    price             = serializers.SerializerMethodField()
    cover_picture_url = serializers.SerializerMethodField()

    class Meta:
        model  = Game
        fields = ('id', 'name', 'developer', 'price', 'cover_picture_url')
    
    def get_price(self, obj):
        return obj.get_actual_price()

    def get_cover_picture_url(self, obj):
        return obj.get_cover_picture()

class BaseStoreObjectSerializer(ModelSerializer):
    games  = serializers.PrimaryKeyRelatedField(many=True, queryset = Game.objects.all())
    user   = serializers.SerializerMethodField(read_only=True)
    action = serializers.CharField(default = None, write_only = True)
    
    def create(self, validated_data):
        validated_data.pop("action", None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if "action" in validated_data:
            if "add" == validated_data["action"]:
                instance.games.add(*validated_data["games"])
            if "remove" == validated_data["action"]:
                instance.games.remove(*validated_data["games"])
            
            validated_data.pop("games", None)
            validated_data.pop("action", None)

        return super().update(instance, validated_data)
    
    def get_user(self, obj):
        return obj.user.get_username()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['games'] = gamesSerializerSimplified(instance.games.all(), many=True).data
        return rep

class CartSerializer(BaseStoreObjectSerializer):
    
    class Meta:
        model = Cart
        fields = ['user', 'games', 'action']
        read_only_fields = ["user"]

class WishlistSerializer(BaseStoreObjectSerializer):
    
    class Meta:
        model = Wishlist
        fields = ['user', 'games', 'action']
        read_only_fields = ["user"]

class GameMediaSerializer(ModelSerializer):
    signed_url = serializers.SerializerMethodField()
    class Meta:
        model = GamesMedia
        fields = ('id', 'media_type', 'signed_url')

    def get_signed_url(self, obj):
        return obj.get_signed_url()
    
class WalletSerializer(ModelSerializer):
    
    class Meta:
        model  = Wallet
        fields = "__all__"

class WalletTransactionSerializer(ModelSerializer):
    
    class Meta:
        model  = WalletTransaction
        fields = "__all__"

class SaleSerializer(serializers.ModelSerializer):
    cover_picture     = serializers.ImageField(write_only=True, allow_null=False)
    sale_end_date     = serializers.DateTimeField(required=False, allow_null=True)
    games             = serializers.CharField(write_only=True, required=True, allow_null=False)
    cover_picture_url = serializers.SerializerMethodField()

    class Meta:
        model  = Sale
        fields = "__all__"

    def validate(self, attrs):
        attrs["games"] = json.loads(attrs["games"])

        if not attrs.get("sale_end_date"):
            attrs["sale_end_date"] = timezone.now() + timedelta(days=14)

        return attrs

    def validate_cover_picture(self, cover_picture):
        sale_name = self.initial_data.get("sale_name")
        if cover_picture:
            valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if cover_picture.content_type not in valid_mime_types:
                raise ValidationError("Only image files (JPEG, PNG, GIF, WEBP, JPG) are allowed.")
            
            safe_path = re.sub(r'[^a-zA-Z0-9\-_/\.]', '', sale_name)
            public_url = upload_file_to_supabase(cover_picture, f"Sale/{safe_path}")
            return public_url
        return None

    def get_cover_picture_url(self, obj):
        return obj.get_cover_picture()

    def create(self, validated_data):
        game_ids = validated_data.pop("games", [])
        sale = super().create(validated_data)
        sale.games.set(game_ids)  
        return sale


class SaleSerializerDetail(SaleSerializer):
    game_objs         = gamesSerializerSimplified(source="games", many=True, read_only=True)