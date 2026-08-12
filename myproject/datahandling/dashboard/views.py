from rest_framework import generics
from stories.models import Story
from stories.serializers import StoryDisplaySerializer

# 1. RETRIEVE the list of all stories (Your Moderation Queue)
class DashboardStoryListView(generics.ListAPIView):
    serializer_class = StoryDisplaySerializer

    def get_queryset(self):
        # Start with all stories, ordered by newest first
        queryset = Story.objects.all().order_by('-created_at')
        
        # Optional: Let Next.js filter by status (e.g., ?status=pending)
        status_param = self.request.query_params.get('status', None)
        if status_param is not None:
            queryset = queryset.filter(status=status_param)
            
        return queryset

# 2. RUD operations for a single specific story
class DashboardStoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Story.objects.all()
    serializer_class = StoryDisplaySerializer
    lookup_field = 'pk' 