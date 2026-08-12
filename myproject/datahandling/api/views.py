from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import DashboardActionRequestSerializer


from stories.models import Story
from .serializers import (
    AdminStoryListSerializer,
    AdminStoryModerationSerializer,
    CommunityStorySerializer,
)
from .serializers import StorySubmissionSerializer


class StorySubmitView(generics.ListCreateAPIView):
    queryset=Story.objects.all()
    serializer_class=StorySubmissionSerializer

class StoryRetrieveTest(generics.RetrieveUpdateDestroyAPIView):
    queryset=Story.objects.all()
    serializer_class=StorySubmissionSerializer
    lookup_field='pk'


class DashboardActionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DashboardActionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        return Response(
            {
                "message": "Request validated successfully.",
                "action": data["action"],
                "target_id": data["target_id"],
            },
            status=status.HTTP_200_OK,
        )