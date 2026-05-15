from rest_framework import serializers
from .models import *
import re
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
        if not data.get("email"):
            raise serializers.ValidationError({"email": "Email is required"})
        if not data.get("password"):
            raise serializers.ValidationError({"password": "Password is required"})
        return data

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            is_active=False
        )
        user.set_password(validated_data['password'])  # 🔥 hash password
        user.save()
        return user