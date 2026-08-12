from rest_framework import serializers
from stories.models import Story

class StorySubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Story
        fields = "__all__"
        read_only_fields = ['status'] 