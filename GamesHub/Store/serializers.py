from .models import Game, Cart, Wishlist
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class gamesSerializer(ModelSerializer):
    publishedDate = serializers.DateField(format="%d/%m/%Y")

    class Meta:
        model = Game
        fields = '__all__'

class gamesSerializerSimplified(ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model  = Game
        fields = ('name', 'developer', 'price')
    
    def get_price(self, obj):
        return obj.get_price()

class cartSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    games = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['user', 'games']

    def get_user(self, obj):
        return obj.user.get_username()

    def get_games(self, obj):
        return [game.get_name() for game in obj.games.all()]
    
class wishlistSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    games = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ['user', 'games']

    def get_user(self, obj):
        return obj.user.get_username()

    def get_games(self, obj):
        return [game.get_name() for game in obj.games.all()]