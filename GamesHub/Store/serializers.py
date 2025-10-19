from .models import Game, Cart
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class gamesSerializer(ModelSerializer):
    publishedDate = serializers.DateField(format="%d/%m/%Y")

    class Meta:
        model = Game
        fields = '__all__'

class cartSerializer(ModelSerializer):
    class Meta:
        model  = Cart
        fields = '__all__'