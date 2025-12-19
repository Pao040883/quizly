"""
Serializers for authentication app.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirmed_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirmed_password')

    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Create new user.
        """
        validated_data.pop('confirmed_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)
