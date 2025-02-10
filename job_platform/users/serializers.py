from rest_framework import serializers
from .models import User  # или импортируйте вашу кастомную модель User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
