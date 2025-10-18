from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
User = get_user_model()

class userSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'default': True}
        }

    
    def validate_password(self, rawPassword):
        return make_password(rawPassword)