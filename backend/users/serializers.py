from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # never return password

    class Meta:
        model = User
        fields = ("id", "username", "password")

    def validate_username(self, value):
        """Ensure username is at least 5 chars and unique."""
        if len(value) < 5:
            raise serializers.ValidationError("Username must be at least 5 characters.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_password(self, value):
        """Ensure password is at least 8 chars."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        return value

    def create(self, validated_data):
        """
        Create a new user with hashed password
        """
        user = User(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid username or password")
        data["user"] = user
        return data
