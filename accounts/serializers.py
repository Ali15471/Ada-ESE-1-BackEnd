from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_password(self, value):
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['username', 'email', 'display_name', 'bio', 'profile_picture']

    def validate_display_name(self, value):
        if len(value) > 50:
            raise serializers.ValidationError("Display name must be 50 characters or less.")
        return value
    
    def validate_bio(self, value):
        if len(value) > 144:
            raise serializers.ValidationError("Bio must be 144 characters or less.")
        return value
