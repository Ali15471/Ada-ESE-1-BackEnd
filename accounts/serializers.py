from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_password(self, value):
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["username", "email", "bio", "profile_picture"]

    def validate_bio(self, value):
        if len(value) > 144:
            raise serializers.ValidationError("Bio must be 144 characters or less.")
        return value

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.profile_picture:
            data["profile_picture"] = obj.profile_picture.url
        return data

    def validate_profile_picture(self, image):
        if not image:
            return image
        if image.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image must be under 2MB.")
        return image
