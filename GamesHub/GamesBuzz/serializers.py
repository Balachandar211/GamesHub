from rest_framework.serializers import ModelSerializer, ValidationError
from .models import GameInteraction, Review
from rest_framework import serializers
from utills.microservices import validate_vote_value, update_voting_field
from django.contrib.contenttypes.models import ContentType
from Store.serializers import gamesSerializerSimplified

REVIEW_CONTENT_TYPE = ContentType.objects.get_for_model(Review)

class GameInteractionSerializer(ModelSerializer):
    class Meta:
        model   = GameInteraction
        exclude = "__all__"

    
class ReviewSerializer(ModelSerializer):
    user            = serializers.SerializerMethodField()
    upvote_review   = serializers.CharField(write_only=True, required=False)
    downvote_review = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = ('id', 'user', 'game', 'comment', 'rating', "upvote", "downvote", "upvote_review", "downvote_review")
        extra_kwargs = {'game': {'read_only': True}}

    def validate(self, attrs):
        if validate_vote_value(attrs, "review"):
            raise ValidationError("Only one of upvote_post or downvote_post can be set.")

        return attrs

    def update(self, instance, validated_data):
        request_user = self.context.get('request_user')
        instance = update_voting_field(instance, validated_data, REVIEW_CONTENT_TYPE, "review", request_user)

        return super().update(instance, validated_data)

    def get_user(self, obj):
        return obj.user.get_username()


class GameInteractionSerializerSimplified(ModelSerializer):
    user   = serializers.SerializerMethodField()
    game   = gamesSerializerSimplified(read_only=True)

    class Meta:
        model = GameInteraction
        fields = ('user', 'game')

    def get_user(self, obj):
        return obj.user.get_username()
    