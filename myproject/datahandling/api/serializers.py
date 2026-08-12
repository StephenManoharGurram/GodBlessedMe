from rest_framework import serializers
from stories.models import Story

class StorySubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Story
        fields = "__all__"
        read_only_fields = ['status'] 


class DashboardActionRequestSerializer(serializers.Serializer):
     ACTION_CHOICES = [
        ("accept", "accept"),
        ("deny", "deny"),
        ("delete", "delete"),
        ]
     action = serializers.ChoiceField(choices=ACTION_CHOICES)
     target_id = serializers.IntegerField()

     def validate(self, data):
        action = data["action"]
        target_id = data.get("target_id")

        if action in ["archive_widget"] and not target_id:
            raise serializers.ValidationError({
                "target_id must be a positive integer."
            })

        return data