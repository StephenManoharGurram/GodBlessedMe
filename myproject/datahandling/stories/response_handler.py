"""
stories/response_handler.py

Standardizes all API responses to a consistent JSON format.
Handles success and error responses with proper HTTP status codes.
"""

from datetime import datetime
from django.http import JsonResponse
from rest_framework import status
from .exceptions import (
    StorySubmissionError,
    ValidationFailedError,
    DuplicateAuthorError,
    StoryNotFoundError,
    AuthorNotFoundError,
    RateLimitError,
    UnauthorizedError
)


class APIResponse:
    """
    Standardizes all API responses.
    
    Success format:
    {
        "success": true,
        "message": "Story submitted successfully",
        "data": {
            "story_id": "uuid",
            "author_id": "uuid",
            "status": "pending",
            "title": "Story Title",
            "created_at": "2026-08-12T10:30:00Z"
        },
        "timestamp": "2026-08-12T10:30:00Z"
    }
    
    Error format:
    {
        "success": false,
        "error_code": "INVALID_EMAIL",
        "message": "Email is not valid",
        "field_errors": {
            "email": ["Invalid email format"]
        },
        "timestamp": "2026-08-12T10:30:00Z"
    }
    """
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat() + "Z"
    
    @staticmethod
    def success(data, message="Request successful", status_code=status.HTTP_200_OK):
        """
        Create a success response.
        
        Args:
            data (dict): Response data to include
            message (str): Success message
            status_code (int): HTTP status code
            
        Returns:
            JsonResponse: Formatted success response
            
        Example:
            return APIResponse.success(
                data={
                    "story_id": "550e8400-e29b-41d4-a716-446655440000",
                    "author_id": "550e8400-e29b-41d4-a716-446655440001",
                    "status": "pending"
                },
                message="Story submitted successfully",
                status_code=201
            )
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": APIResponse.get_timestamp()
        }
        return JsonResponse(response, status=status_code)
    
    @staticmethod
    def error(
        error_code,
        message,
        field_errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
        details=None
    ):
        """
        Create an error response.
        
        Args:
            error_code (str): Machine-readable error code (e.g., "INVALID_EMAIL")
            message (str): Human-readable error message
            field_errors (dict): Field-level validation errors
                Example: {"email": ["Invalid format"], "title": ["Too short"]}
            status_code (int): HTTP status code
            details (dict): Additional details (optional)
            
        Returns:
            JsonResponse: Formatted error response
            
        Example:
            return APIResponse.error(
                error_code="VALIDATION_FAILED",
                message="Validation failed for 2 field(s)",
                field_errors={
                    "email": ["Invalid email"],
                    "title": ["Too short"]
                },
                status_code=400
            )
        """
        response = {
            "success": False,
            "error_code": error_code,
            "message": message,
            "timestamp": APIResponse.get_timestamp()
        }
        
        if field_errors:
            response["field_errors"] = field_errors
        
        if details:
            response["details"] = details
        
        return JsonResponse(response, status=status_code)
    
    @staticmethod
    def from_exception(exc):
        """
        Create response from exception object.
        Automatically determines status code based on exception type.
        
        Args:
            exc (Exception): Exception to convert to response
            
        Returns:
            JsonResponse: Formatted error response
            
        Example:
            try:
                # some operation
            except StorySubmissionError as e:
                return APIResponse.from_exception(e)
        """
        
        # Handle ValidationFailedError (multiple field errors)
        if isinstance(exc, ValidationFailedError):
            return APIResponse.error(
                error_code=exc.error_code,
                message=exc.message,
                field_errors=exc.details.get("field_errors", {}),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle DuplicateAuthorError (author already exists - not an error)
        if isinstance(exc, DuplicateAuthorError):
            return APIResponse.error(
                error_code=exc.error_code,
                message=exc.message,
                status_code=status.HTTP_200_OK  # Info message, not an error
            )
        
        # Handle StoryNotFoundError (404)
        if isinstance(exc, StoryNotFoundError):
            return APIResponse.error(
                error_code=exc.error_code,
                message=exc.message,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Handle AuthorNotFoundError (404)
        if isinstance(exc, AuthorNotFoundError):
            return APIResponse.error(
                error_code=exc.error_code,
                message=exc.message,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Handle RateLimitError (429)
        if isinstance(exc, RateLimitError):
            return APIResponse.error(
                error_code=exc.error_code,
                message=exc.message,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                details=exc.details
            )
        
        # Handle UnauthorizedError (403)
        if isinstance(exc, UnauthorizedError):
            return APIResponse.error(
                error_code=exc.error_code,
                message=exc.message,
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Handle all other StorySubmissionError subclasses (400)
        if isinstance(exc, StorySubmissionError):
            return APIResponse.error(
                error_code=exc.error_code,
                message=exc.message,
                status_code=status.HTTP_400_BAD_REQUEST,
                details=exc.details if exc.details else None
            )
        
        # Handle unexpected exceptions (500)
        return APIResponse.error(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"exception": str(type(exc).__name__)}
        )


class SuccessResponses:
    """
    Predefined success response messages and data formatters.
    Used by views to create consistent responses.
    """
    
    @staticmethod
    def story_created(story_obj):
        """
        Format response for successful story creation.
        
        Args:
            story_obj (Story): Story model instance
            
        Returns:
            dict: Formatted data for response
        """
        return {
            "story_id": str(story_obj.id),
            "author_id": str(story_obj.author.id),
            "title": story_obj.title,
            "status": story_obj.status,
            "created_at": story_obj.created_at.isoformat() + "Z",
            "updated_at": story_obj.updated_at.isoformat() + "Z"
        }
    
    @staticmethod
    def author_and_story(author_obj, story_obj):
        """
        Format response with both author and story details.
        
        Args:
            author_obj (Author): Author model instance
            story_obj (Story): Story model instance
            
        Returns:
            dict: Formatted data for response
        """
        return {
            "author": {
                "id": str(author_obj.id),
                "email": author_obj.email,
                "first_name": author_obj.first_name,
                "last_name": author_obj.last_name,
                "phone": author_obj.phone,
                "created_at": author_obj.created_at.isoformat() + "Z"
            },
            "story": {
                "id": str(story_obj.id),
                "title": story_obj.title,
                "status": story_obj.status,
                "created_at": story_obj.created_at.isoformat() + "Z",
                "updated_at": story_obj.updated_at.isoformat() + "Z"
            }
        }
    
    @staticmethod
    def story_deleted(story_id):
        """
        Format response for successful story deletion.
        
        Args:
            story_id (UUID): Story ID that was deleted
            
        Returns:
            dict: Formatted data for response
        """
        return {
            "story_id": str(story_id),
            "message": "Story has been deleted successfully"
        }
    
    @staticmethod
    def story_updated(story_obj):
        """
        Format response for successful story update.
        
        Args:
            story_obj (Story): Updated Story model instance
            
        Returns:
            dict: Formatted data for response
        """
        return {
            "story_id": str(story_obj.id),
            "title": story_obj.title,
            "status": story_obj.status,
            "updated_at": story_obj.updated_at.isoformat() + "Z"
        }
    
    @staticmethod
    def stories_list(stories_queryset, page=None, total=None):
        """
        Format response for list of stories.
        
        Args:
            stories_queryset: QuerySet of Story objects
            page (int): Current page number (optional)
            total (int): Total number of stories (optional)
            
        Returns:
            dict: Formatted data for response
        """
        stories_data = [
            {
                "story_id": str(story.id),
                "author_id": str(story.author.id),
                "author_name": f"{story.author.first_name} {story.author.last_name}",
                "title": story.title,
                "status": story.status,
                "created_at": story.created_at.isoformat() + "Z"
            }
            for story in stories_queryset
        ]
        
        result = {"stories": stories_data}
        if page is not None:
            result["page"] = page
        if total is not None:
            result["total"] = total
        
        return result


class ErrorResponses:
    """
    Predefined error messages.
    Used by views to raise exceptions with consistent messages.
    """
    
    # Validation errors
    INVALID_EMAIL = "Invalid email format"
    INVALID_NAME = "Name contains invalid characters"
    INVALID_TITLE = "Story title is invalid"
    INVALID_STORY = "Story content is invalid"
    INVALID_PHONE = "Phone number format is invalid"
    
    # Database errors
    STORY_NOT_FOUND = "Story not found"
    AUTHOR_NOT_FOUND = "Author not found"
    DATABASE_ERROR = "Database operation failed"
    
    # Auth errors
    UNAUTHORIZED = "You are not authorized to perform this action"
    
    # Rate limiting
    RATE_LIMIT = "Too many requests. Please try again later."