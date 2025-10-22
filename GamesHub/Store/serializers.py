from .models import Game, Cart
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class gamesSerializer(ModelSerializer):
    publishedDate = serializers.DateField(format="%d/%m/%Y")

    class Meta:
        model = Game
        fields = '__all__'

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