from .models import User
from rest_framework.serializers import ModelSerializer

class userSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
