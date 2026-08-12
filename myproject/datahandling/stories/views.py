from rest_framework import generics
from .models import Story
from .serializers import StorySubmissionSerializer, StoryDisplaySerializer

# Handles the POST request (Creation)
class StoryCreateAPIView(generics.CreateAPIView):
    serializer_class = StorySubmissionSerializer

# Handles the GET request (Associates/Retrieves stories linked to a specific user ID)
class UserStoryListAPIView(generics.ListAPIView):
    serializer_class = StoryDisplaySerializer

    def get_queryset(self):
        # Extracts the author's UUID from the URL and filters the stories
        author_id = self.kwargs.get('author_id')
        return Story.objects.filter(author__id=author_id)