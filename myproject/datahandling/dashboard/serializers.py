from rest_framework import serializers
from stories.models import Story, Author


class AuthorDetailSerializer(serializers.ModelSerializer):
    """Serialize author information for admin views"""
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'id']


class DashboardStoryListSerializer(serializers.ModelSerializer):
    """Serializer for admin list view - minimal fields for moderation queue"""
    author_name = serializers.SerializerMethodField()
    author_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = ['id', 'title', 'author_name', 'author_email', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"

    def get_author_email(self, obj):
        return obj.author.email


class DashboardStoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for admin detail view - full story content + author details"""
    author = AuthorDetailSerializer(read_only=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = ['id', 'title', 'story', 'author', 'author_name', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"