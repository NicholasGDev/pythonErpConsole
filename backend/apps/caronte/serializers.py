# backend/apps/caronte/serializers.py
from rest_framework import serializers
from apps.caronte.models import User, UserData


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserData
        fields = ['city', 'country', 'address', 'phone_number', 'date_of_birth']


class UserSerializer(serializers.ModelSerializer):
    user_data = UserDataSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'name', 'email', 'is_active', 'is_staff',
                  'force_password_change', 'date_joined', 'user_data']


class CreateUserSerializer(serializers.Serializer):
    name      = serializers.CharField(max_length=150)
    email     = serializers.EmailField()
    password  = serializers.CharField(write_only=True, min_length=8)
    user_data = UserDataSerializer(required=False)