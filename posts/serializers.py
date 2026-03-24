from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author_username",
            "created_at",
            "updated_at",
            "cover_image",
            "status",
        ]
        read_only_fields = ["id", "author_username", "created_at", "updated_at"]

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long."
            )
        return value

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Content must be at least 10 characters long."
            )
        return value
