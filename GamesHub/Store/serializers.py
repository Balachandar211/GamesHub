from .models import Game, Cart, Wishlist, GamesMedia, Wallet, WalletTransaction
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from utills.storage_supabase import upload_file_to_supabase
from rest_framework.exceptions import ValidationError
from utills.storage_supabase import supabase
from utills.game_media_update import get_cover_url
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

class CartSerializer(ModelSerializer):
    games  = serializers.PrimaryKeyRelatedField(many=True, queryset = Game.objects.all())
    user   = serializers.SerializerMethodField(read_only=True)
    action = serializers.CharField(default = None, write_only = True)
    
    class Meta:
        model = Cart
        fields = ['user', 'games', 'action']
        read_only_fields = ["user"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
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
    
class WishlistSerializer(ModelSerializer):
    games  = serializers.PrimaryKeyRelatedField(many=True, queryset = Game.objects.all())
    user   = serializers.SerializerMethodField(read_only=True)
    action = serializers.CharField(default = None, write_only = True)
    
    class Meta:
        model = Wishlist
        fields = ['user', 'games', 'action']
        read_only_fields = ["user"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
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



class GameMediaSerializer(ModelSerializer):
    signed_url = serializers.SerializerMethodField()
    class Meta:
        model = GamesMedia
        fields = ('id', 'media_type', 'signed_url')

    def get_signed_url(self, obj):
        if obj.url is not None and obj.media_type != 2:
            url_path = obj.url.split("GamesHubMedia/")[1]
            result = supabase.storage.from_("GamesHubMedia").create_signed_url(url_path, 600)
            return result["signedURL"]
        return obj.url
    
class WalletSerializer(ModelSerializer):
    
    class Meta:
        model  = Wallet
        fields = "__all__"

class WalletTransactionSerializer(ModelSerializer):
    
    class Meta:
        model  = WalletTransaction
        fields = "__all__"
