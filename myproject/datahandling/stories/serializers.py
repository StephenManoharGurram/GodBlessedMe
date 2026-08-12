from rest_framework import serializers
from .models import Author, Story

class StorySubmissionSerializer(serializers.ModelSerializer):
    # These fields don't exist directly on the Story model, 
    # so we define them as write_only fields to accept them from Next.js
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True, max_length=100)
    last_name = serializers.CharField(write_only=True, max_length=100)
    phone = serializers.CharField(write_only=True, max_length=12, required=False, allow_blank=True)

    class Meta:
        model = Story
        
        exclude = ['author']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # 1. Pop out the Author data from the payload
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        phone = validated_data.pop('phone', '')

        # 2. Get or create the Author using the email
        author_instance, created = Author.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone
            }
        )

        # 3. Create the Story and link the Foreign Key
        story = Story.objects.create(author=author_instance, **validated_data)
        return story

# A simple serializer for when you want to retrieve a user's stories
class StoryDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'title', 'story', 'status', 'created_at','author_name']

        # This method computes the author_name field above
    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"