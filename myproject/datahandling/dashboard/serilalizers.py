from rest_framework import serializers
from .models import Story
"""


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
        return value"""

# Display serializer for retrieving stories
class StoryDisplaySerializer(serializers.ModelSerializer):
    # 1. YOU MUST DECLARE THE FIELD HERE!
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Story
        # 2. Now DRF knows what 'author_name' is when it sees it in this list
        fields = ['id', 'title', 'story', 'status', 'created_at', 'author_name']

    # 3. This method calculates the value for the field above
    def get_author_name(self, obj):
        # We use obj.author.first_name to fetch the name across the Foreign Key
        return f"{obj.author.first_name} {obj.author.last_name}"