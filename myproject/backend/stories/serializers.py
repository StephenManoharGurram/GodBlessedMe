from rest_framework import serializers
from .models import Story


class StorySubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["title", "content", "author_name"]


class PublicStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "title", "content", "author_name", "submitted_at"]


class AdminStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "title", "content", "author_name", "submitted_at", "status", "ip_address"]


class StoryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["status"]

    def validate_status(self, value):
        valid_statuses = ["pending", "approved", "denied"]
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status.")
        return value