from rest_framework import generics
from stories.models import Story
from stories.serializers import StoryDisplaySerializer
from rest_framework.generics import ListAPIView
from .serializers import StoryListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class StoryListView(generics.ListAPIView):
    serializer_class = StoryListSerializer
    queryset = Story.objects.select_related("author").all().order_by("-created_at")


class DashboardActionReceiverAPIView(APIView):
    def post(self, request, *args, **kwargs):
        action = request.data.get("action")
        target_id = request.data.get("target_id")

        return Response(
            {
                "message": "Dashboard received the request.",
                "received_action": action,
                "received_target_id": target_id,
            },
            status=status.HTTP_200_OK,
        )
    
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