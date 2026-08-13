from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.core.paginator import Paginator
from stories.models import Story
from dashboard.serializers import DashboardStoryListSerializer, DashboardStoryDetailSerializer
from dashboard.services import StoryService
from .serializers import StorySubmissionSerializer


class StorySubmitView(generics.ListCreateAPIView):
    queryset=Story.objects.all()
    serializer_class=StorySubmissionSerializer

"""
API App Views - DRF Gateway
ALL communication between frontend and backend routes through here.
"""

class StoriesFetchAllAPIView(generics.ListAPIView):
    """
    API Endpoint: GET /api/v1/stories/fetch-all/
    
    Fetch all stories for admin moderation queue
    - Supports pagination (default: 20 per page)
    - Supports filtering by status (pending, approved, denied)
    - Returns minimal fields for list view
    """
    serializer_class = DashboardStoryListSerializer
    pagination_class = None  # We'll handle pagination manually below

    def get_queryset(self):
        """Get stories based on filters"""
        filters = {}
        
        # Extract status filter from query params
        status_param = self.request.query_params.get('status')
        if status_param:
            filters['status'] = status_param
        
        # Extract search filter from query params
        search_param = self.request.query_params.get('search')
        if search_param:
            filters['search'] = search_param
        
        # Call dashboard service to get queryset
        return StoryService.fetch_all_stories(filters=filters)

    def list(self, request, *args, **kwargs):
        """Override list to add custom pagination"""
        queryset = self.get_queryset()
        
        # Pagination
        page_num = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        
        try:
            page_size = int(page_size)
            if page_size < 1 or page_size > 100:
                page_size = 20
        except (ValueError, TypeError):
            page_size = 20
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page_num)
        except Exception:
            page_obj = paginator.page(1)
        
        serializer = self.get_serializer(page_obj.object_list, many=True)
        
        return Response({
            'count': paginator.count,
            'next': f"?page={page_obj.next_page_number()}" if page_obj.has_next() else None,
            'previous': f"?page={page_obj.previous_page_number()}" if page_obj.has_previous() else None,
            'results': serializer.data
        })


class StoriesDetailAPIView(APIView):
    """
    API Endpoints:
    - GET /api/v1/stories/<story_id>/  - Fetch single story
    - PATCH /api/v1/stories/<story_id>/ - Update story status
    - DELETE /api/v1/stories/<story_id>/ - Delete story
    """

    def get(self, request, story_id):
        """GET - Fetch single story details"""
        try:
            story = StoryService.get_story_detail(story_id)
            serializer = DashboardStoryDetailSerializer(story)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, story_id):
        """PATCH - Update story status"""
        try:
            new_status = request.data.get('status')
            
            if not new_status:
                return Response(
                    {'error': 'Status field is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Call dashboard service to update status
            story = StoryService.update_story_status(story_id, new_status)
            serializer = DashboardStoryDetailSerializer(story)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, story_id):
        """DELETE - Delete a story"""
        try:
            result = StoryService.delete_story(story_id)
            return Response(
                result,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )