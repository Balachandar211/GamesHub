from rest_framework.serializers import ModelSerializer
from .models import GameInteraction
from rest_framework import serializers
from Store.serializers import gamesSerializerSimplified

class GameInteractionSerializer(ModelSerializer):
    class Meta:
        model = GameInteraction
        fields = '__all__'

        def validate_rating(self, value):
            if value not in [1, 2, 3, 4, 5]:
                raise serializers.ValidationError("Rating must be between 1 and 5.")
            return value

    
class GameInteractionSerializerSimplified(ModelSerializer):
    user   = serializers.SerializerMethodField()
    game   = gamesSerializerSimplified(read_only=True)

    class Meta:
        model = GameInteraction
        fields = ('user', 'game', 'comment', 'rating')

    def get_user(self, obj):
        return obj.user.get_username()
    