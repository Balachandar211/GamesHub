from rest_framework.serializers import ModelSerializer
from .models import GameInteraction
from rest_framework import serializers

class GameInteractionSerializer(ModelSerializer):
    class Meta:
        model = GameInteraction
        fields = '__all__'

        def validate_rating(self, value):
            if value not in [1, 2, 3, 4, 5]:
                return serializers.ValidationError("Rating must be between 1 and 5.")
            return value

    
class GameInteractionSerializerSimplified(ModelSerializer):
    user   = serializers.SerializerMethodField()

    class Meta:
        model = GameInteraction
        fields = ('user', 'comment', 'rating')

    def get_user(self, obj):
        return obj.user.get_username()