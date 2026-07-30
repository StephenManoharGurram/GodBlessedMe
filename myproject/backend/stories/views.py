import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission
from .models import Story
from .serializers import (
    StorySubmitSerializer,
    PublicStorySerializer,
    AdminStorySerializer,
    StoryStatusSerializer,
)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class IsDashboardSecret(BasePermission):
    message = "Admin access denied."

    def has_permission(self, request, view):
        secret = os.environ.get("DASHBOARD_SECRET", "")
        incoming = request.headers.get("X-Dashboard-Secret", "")
        return bool(secret) and incoming == secret


class PublicStoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        stories = Story.objects.filter(status="approved").order_by("-submitted_at")
        serializer = PublicStorySerializer(stories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicStorySubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StorySubmitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ip_address=get_client_ip(request), status="pending")
            return Response(
                {"message": "Story submitted successfully and is awaiting review."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminStoryListView(APIView):
    permission_classes = [IsDashboardSecret]

    def get(self, request):
        stories = Story.objects.all().order_by("-submitted_at")
        serializer = AdminStorySerializer(stories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminStoryDetailView(APIView):
    permission_classes = [IsDashboardSecret]

    def get_object(self, pk):
        try:
            return Story.objects.get(pk=pk)
        except Story.DoesNotExist:
            return None

    def patch(self, request, pk):
        story = self.get_object(pk)
        if not story:
            return Response(
                {"detail": "Story not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StoryStatusSerializer(story, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                AdminStorySerializer(story).data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        story = self.get_object(pk)
        if not story:
            return Response(
                {"detail": "Story not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        story.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)