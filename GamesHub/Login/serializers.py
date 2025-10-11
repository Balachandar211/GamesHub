from .models import User
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password

class userSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'passWord': {'write_only': True}
        }

    
    def validate_passWord(self, rawPassword):
        return make_password(rawPassword)