from .models import Game
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class gamesSerializer(ModelSerializer):
    publishedDate = serializers.DateField(format="%d/%m/%Y")

    class Meta:
        model = Game
        fields = '__all__'