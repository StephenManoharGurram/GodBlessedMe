"""
stories/views.py

API endpoints for story submission and retrieval.
All views use the service layer for business logic.
All responses are standardized via response_handler.
All operations are logged via logger.
"""

import uuid
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import status as http_status
from django.http import JsonResponse

from .models import Story, Author
from .serializers import (
    StorySubmissionSerializer,
    StoryDisplaySerializer,
    DashboardStoryListSerializer,
    DashboardStoryDetailSerializer,
    StoryStatusUpdateSerializer
)
from .services import (
    StorySubmissionService,
    StoryRetrievalService,
    StoryModerationService
)
from .response_handler import APIResponse, SuccessResponses, ErrorResponses
from .exceptions import (
    StorySubmissionError,
    ValidationFailedError,
    StoryNotFoundError
)
from .logger import StoryLogger


# ============================================================================
# USER ENDPOINTS (Story Submission & Retrieval)
# ============================================================================

class StoryCreateAPIView(APIView):
    """
    POST /api/v1/stories/submit/
    
    Endpoint for users to submit a new story.
    
    Input (JSON):
    {
        "email": "john@gmail.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "555-1234",  (optional)
        "title": "My Story Title",
        "story": "This is the content of my story..."
    }
    
    Output (Success - 201):
    {
        "success": true,
        "message": "Story submitted successfully",
        "data": {
            "story_id": "uuid",
            "author_id": "uuid",
            "status": "pending",
            "title": "My Story Title",
            "created_at": "2026-08-12T10:30:00Z",
            "updated_at": "2026-08-12T10:30:00Z"
        },
        "timestamp": "2026-08-12T10:30:00Z"
    }
    
    Output (Error - 400):
    {
        "success": false,
        "error_code": "VALIDATION_FAILED",
        "message": "Validation failed for 2 field(s)",
        "field_errors": {
            "email": ["Invalid email format"],
            "title": ["Too short"]
        },
        "timestamp": "2026-08-12T10:30:00Z"
    }
    """
    
    def post(self, request):
        """
        Handle story submission.
        
        Args:
            request: HTTP request with JSON body
            
        Returns:
            JsonResponse: Standardized success or error response
        """
        try:
            # Generate request ID for tracking
            request_id = str(uuid.uuid4())
            
            # Get client IP address
            ip_address = self._get_client_ip(request)
            
            # Get submission data
            data = request.data
            
            # Use service layer to submit story
            result = StorySubmissionService.submit_story(
                data=data,
                ip_address=ip_address,
                request_id=request_id
            )
            
            # Return success response
            return APIResponse.success(
                data=result,
                message="Story submitted successfully",
                status_code=http_status.HTTP_201_CREATED
            )
        
        except ValidationFailedError as e:
            # Validation failed - return field errors
            return APIResponse.error(
                error_code=e.error_code,
                message=e.message,
                field_errors=e.details.get("field_errors", {}),
                status_code=http_status.HTTP_400_BAD_REQUEST
            )
        
        except StorySubmissionError as e:
            # Other submission errors - use response handler
            return APIResponse.from_exception(e)
        
        except Exception as e:
            # Unexpected error
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="STORY_SUBMISSION",
                exception=e
            )
            return APIResponse.from_exception(e)
    
    @staticmethod
    def _get_client_ip(request):
        """
        Extract client IP address from request.
        
        Args:
            request: HTTP request
            
        Returns:
            str: Client IP address or None
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserStoryListAPIView(ListAPIView):
    """
    GET /api/v1/stories/user/<author_id>/
    
    Retrieve all stories submitted by a specific user.
    
    Path Parameters:
    - author_id: UUID of the author
    
    Output (Success - 200):
    {
        "success": true,
        "message": "Stories retrieved successfully",
        "data": {
            "stories": [
                {
                    "id": "story-uuid",
                    "author_id": "author-uuid",
                    "author_name": "John Doe",
                    "title": "My Story",
                    "story": "Story content...",
                    "status": "pending",
                    "created_at": "2026-08-12T10:30:00Z",
                    "updated_at": "2026-08-12T10:30:00Z"
                },
                ...
            ]
        },
        "timestamp": "2026-08-12T10:30:00Z"
    }
    
    Output (Error - 404):
    {
        "success": false,
        "error_code": "AUTHOR_NOT_FOUND",
        "message": "Author with ID '...' not found.",
        "timestamp": "2026-08-12T10:30:00Z"
    }
    """
    
    serializer_class = StoryDisplaySerializer
    
    def get_queryset(self):
        """
        Get all stories for a specific author.
        
        Args:
            request: HTTP request
            
        Returns:
            QuerySet: Stories for the author
        """
        author_id = self.kwargs.get('author_id')
        return Story.objects.filter(author__id=author_id).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Override list to use standardized response format.
        
        Args:
            request: HTTP request
            
        Returns:
            JsonResponse: Standardized response
        """
        try:
            author_id = self.kwargs.get('author_id')
            request_id = str(uuid.uuid4())
            
            # Use service to get stories
            stories = StoryRetrievalService.get_user_stories(
                author_id=author_id,
                request_id=request_id
            )
            
            # Serialize stories
            serializer = self.get_serializer(stories, many=True)
            
            # Format response
            data = {
                "stories": serializer.data,
                "total": stories.count()
            }
            
            return APIResponse.success(
                data=data,
                message="Stories retrieved successfully",
                status_code=http_status.HTTP_200_OK
            )
        
        except StorySubmissionError as e:
            return APIResponse.from_exception(e)
        
        except Exception as e:
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="GET_USER_STORIES",
                exception=e
            )
            return APIResponse.from_exception(e)


# ============================================================================
# ADMIN ENDPOINTS (Dashboard & Moderation)
# ============================================================================

class StoriesFetchAllAPIView(ListAPIView):
    """
    GET /api/v1/stories/fetch-all/
    
    Retrieve all stories for admin moderation queue.
    Supports filtering and pagination.
    
    Query Parameters:
    - status: Filter by status (pending, approved, denied)
    - page: Page number (default: 1)
    - page_size: Stories per page (default: 20, max: 100)
    
    Output (Success - 200):
    {
        "success": true,
        "message": "Stories retrieved successfully",
        "data": {
            "stories": [
                {
                    "id": "story-uuid",
                    "author_id": "author-uuid",
                    "title": "Story Title",
                    "author_name": "John Doe",
                    "author_email": "john@gmail.com",
                    "status": "pending",
                    "created_at": "2026-08-12T10:30:00Z",
                    "updated_at": "2026-08-12T10:30:00Z"
                },
                ...
            ],
            "total": 42,
            "page": 1,
            "page_size": 20
        },
        "timestamp": "2026-08-12T10:30:00Z"
    }
    """
    
    serializer_class = DashboardStoryListSerializer
    
    def get_queryset(self):
        """
        Get all stories with optional filters.
        
        Returns:
            QuerySet: Stories matching filters
        """
        queryset = Story.objects.select_related('author').order_by('-created_at')
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list to add pagination and standardized response.
        
        Args:
            request: HTTP request
            
        Returns:
            JsonResponse: Standardized response with pagination
        """
        try:
            request_id = str(uuid.uuid4())
            queryset = self.get_queryset()
            
            # Pagination
            page_num = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            # Validate page_size
            if page_size < 1 or page_size > 100:
                page_size = 20
            
            # Calculate pagination
            total_count = queryset.count()
            start = (page_num - 1) * page_size
            end = start + page_size
            
            paginated_stories = queryset[start:end]
            
            # Serialize
            serializer = self.get_serializer(paginated_stories, many=True)
            
            # Format response
            data = {
                "stories": serializer.data,
                "total": total_count,
                "page": page_num,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
            
            return APIResponse.success(
                data=data,
                message="Stories retrieved successfully",
                status_code=http_status.HTTP_200_OK
            )
        
        except Exception as e:
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="FETCH_ALL_STORIES",
                exception=e
            )
            return APIResponse.from_exception(e)


class StoriesDetailAPIView(APIView):
    """
    GET /api/v1/stories/<story_id>/
    PATCH /api/v1/stories/<story_id>/
    DELETE /api/v1/stories/<story_id>/
    
    Retrieve, update, or delete a specific story (admin).
    """
    
    def get(self, request, story_id):
        """
        GET - Retrieve single story details.
        
        Output (Success - 200):
        {
            "success": true,
            "message": "Story retrieved successfully",
            "data": {
                "id": "story-uuid",
                "title": "Story Title",
                "story": "Full story content...",
                "author": {
                    "id": "author-uuid",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@gmail.com",
                    "phone": "555-1234",
                    "created_at": "2026-08-12T10:30:00Z",
                    "updated_at": "2026-08-12T10:30:00Z"
                },
                "author_name": "John Doe",
                "status": "pending",
                "created_at": "2026-08-12T10:30:00Z",
                "updated_at": "2026-08-12T10:30:00Z"
            },
            "timestamp": "2026-08-12T10:30:00Z"
        }
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Use service to get story
            story = StoryRetrievalService.get_story_by_id(
                story_id=story_id,
                request_id=request_id
            )
            
            # Serialize story
            serializer = DashboardStoryDetailSerializer(story)
            
            return APIResponse.success(
                data=serializer.data,
                message="Story retrieved successfully",
                status_code=http_status.HTTP_200_OK
            )
        
        except StorySubmissionError as e:
            return APIResponse.from_exception(e)
        
        except Exception as e:
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="GET_STORY_DETAIL",
                exception=e
            )
            return APIResponse.from_exception(e)
    
    def patch(self, request, story_id):
        """
        PATCH - Update story status.
        
        Input (JSON):
        {
            "status": "approved"  (or "pending", "denied")
        }
        
        Output (Success - 200):
        {
            "success": true,
            "message": "Story updated successfully",
            "data": {
                "story_id": "uuid",
                "title": "Story Title",
                "status": "approved",
                "updated_at": "2026-08-12T10:30:00Z"
            },
            "timestamp": "2026-08-12T10:30:00Z"
        }
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Validate input
            serializer = StoryStatusUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return APIResponse.error(
                    error_code="INVALID_INPUT",
                    message="Invalid status provided",
                    field_errors=serializer.errors,
                    status_code=http_status.HTTP_400_BAD_REQUEST
                )
            
            new_status = serializer.validated_data['status']
            
            # Use service to update status
            story = StoryModerationService.update_story_status(
                story_id=story_id,
                new_status=new_status,
                request_id=request_id
            )
            
            # Format response
            data = SuccessResponses.story_updated(story)
            
            return APIResponse.success(
                data=data,
                message="Story updated successfully",
                status_code=http_status.HTTP_200_OK
            )
        
        except StorySubmissionError as e:
            return APIResponse.from_exception(e)
        
        except Exception as e:
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="UPDATE_STORY_STATUS",
                exception=e
            )
            return APIResponse.from_exception(e)
    
    def delete(self, request, story_id):
        """
        DELETE - Delete a story permanently.
        
        Output (Success - 200):
        {
            "success": true,
            "message": "Story deleted successfully",
            "data": {
                "story_id": "uuid",
                "message": "Story 'Title' has been deleted successfully"
            },
            "timestamp": "2026-08-12T10:30:00Z"
        }
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Use service to delete story
            result = StoryModerationService.delete_story(
                story_id=story_id,
                request_id=request_id
            )
            
            return APIResponse.success(
                data=result,
                message="Story deleted successfully",
                status_code=http_status.HTTP_200_OK
            )
        
        except StorySubmissionError as e:
            return APIResponse.from_exception(e)
        
        except Exception as e:
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="DELETE_STORY",
                exception=e
            )
            return APIResponse.from_exception(e)


class StoryPendingQueueAPIView(ListAPIView):
    """
    GET /api/v1/stories/pending-queue/
    
    Retrieve pending stories for admin moderation queue.
    Ordered by created_at (oldest first).
    
    Output (Success - 200):
    {
        "success": true,
        "message": "Pending stories retrieved successfully",
        "data": {
            "stories": [
                {
                    "id": "story-uuid",
                    "author_id": "author-uuid",
                    "title": "Story Title",
                    "author_name": "John Doe",
                    "author_email": "john@gmail.com",
                    "status": "pending",
                    "created_at": "2026-08-12T10:30:00Z",
                    "updated_at": "2026-08-12T10:30:00Z"
                },
                ...
            ],
            "total": 15
        },
        "timestamp": "2026-08-12T10:30:00Z"
    }
    """
    
    serializer_class = DashboardStoryListSerializer
    
    def get_queryset(self):
        """Get all pending stories"""
        return Story.objects.filter(status='pending').select_related('author').order_by('created_at')
    
    def list(self, request, *args, **kwargs):
        """Override list to use standardized response format"""
        try:
            request_id = str(uuid.uuid4())
            
            stories = StoryModerationService.get_pending_stories(
                request_id=request_id
            )
            
            serializer = self.get_serializer(stories, many=True)
            
            data = {
                "stories": serializer.data,
                "total": stories.count()
            }
            
            return APIResponse.success(
                data=data,
                message="Pending stories retrieved successfully",
                status_code=http_status.HTTP_200_OK
            )
        
        except StorySubmissionError as e:
            return APIResponse.from_exception(e)
        
        except Exception as e:
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="GET_PENDING_QUEUE",
                exception=e
            )
            return APIResponse.from_exception(e)


class StoryApprovedListAPIView(ListAPIView):
    """
    GET /api/v1/stories/approved/
    
    Retrieve approved (published) stories for public view.
    Ordered by created_at (newest first).
    """
    
    serializer_class = DashboardStoryListSerializer
    
    def get_queryset(self):
        """Get all approved stories"""
        return Story.objects.filter(status='approved').select_related('author').order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """Override list to use standardized response format"""
        try:
            request_id = str(uuid.uuid4())
            
            stories = StoryModerationService.get_approved_stories(
                request_id=request_id
            )
            
            serializer = self.get_serializer(stories, many=True)
            
            data = {
                "stories": serializer.data,
                "total": stories.count()
            }
            
            return APIResponse.success(
                data=data,
                message="Approved stories retrieved successfully",
                status_code=http_status.HTTP_200_OK
            )
        
        except StorySubmissionError as e:
            return APIResponse.from_exception(e)
        
        except Exception as e:
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                operation="GET_APPROVED_STORIES",
                exception=e
            )
            return APIResponse.from_exception(e)