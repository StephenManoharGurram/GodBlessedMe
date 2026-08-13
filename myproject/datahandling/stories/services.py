"""
stories/services.py

Business logic layer for story submission and management.
Orchestrates validation, author creation, story creation, and logging.
All views use this service layer.
"""

import time
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Author, Story
from .validator import validate_story_submission, ValidationErrorList, ValidationError as ValidatorError
from .exceptions import (
    ValidationFailedError,
    InvalidAuthorError,
    InvalidStoryError,
    DuplicateAuthorError,
    StoryNotFoundError,
    AuthorNotFoundError,
    DatabaseError
)
from .logger import StoryLogger, LogSummary


class StorySubmissionService:
    """
    Handles complete story submission workflow.
    
    Flow:
    1. Validate input data
    2. Get or create Author
    3. Create Story linked to Author
    4. Log all operations
    5. Return story with author relationship
    """
    
    @staticmethod
    def submit_story(data, ip_address=None, request_id=None):
        """
        Complete story submission workflow.
        
        Args:
            data (dict): Submission data with keys:
                - email
                - first_name
                - last_name
                - phone (optional)
                - title
                - story
            ip_address (str): Client IP address (optional)
            request_id (str): Unique request ID (optional)
        
        Returns:
            dict: Submission result with story_id, author_id, etc.
            
        Raises:
            ValidationFailedError: If validation fails
            InvalidAuthorError: If author creation fails
            InvalidStoryError: If story creation fails
            DatabaseError: If database operation fails
        
        Example:
            result = StorySubmissionService.submit_story(
                data={
                    'email': 'john@gmail.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'title': 'My Story',
                    'story': 'This is my story...'
                },
                ip_address='192.168.1.1',
                request_id='req-12345'
            )
            # Returns:
            # {
            #     'story_id': 'uuid',
            #     'author_id': 'uuid',
            #     'status': 'pending',
            #     'title': 'My Story',
            #     'created_at': 'timestamp'
            # }
        """
        start_time = time.time()
        email = data.get('email')
        
        try:
            # ===== STEP 1: Log submission attempt =====
            StoryLogger.log_submission_attempt(email, ip_address, request_id)
            
            # ===== STEP 2: Validate input data =====
            try:
                cleaned_data = validate_story_submission(data)
            except ValidationErrorList as e:
                # Validation failed with multiple field errors
                StoryLogger.log_validation_failure(email, e.field_errors, request_id)
                raise ValidationFailedError(e.field_errors)
            except ValidatorError as e:
                # Single validator error
                field_errors = {e.field or "unknown": [e.message]}
                StoryLogger.log_validation_failure(email, field_errors, request_id)
                raise ValidationFailedError(field_errors)
            
            # Log validation success
            StoryLogger.log_validation_success(
                email=cleaned_data['email'],
                title=cleaned_data['title'],
                request_id=request_id
            )
            
            # ===== STEP 3: Get or create Author =====
            author, is_new = StorySubmissionService._get_or_create_author(
                email=cleaned_data['email'],
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                phone=cleaned_data.get('phone', ''),
                request_id=request_id
            )
            
            # ===== STEP 4: Create Story =====
            story = StorySubmissionService._create_story(
                author=author,
                title=cleaned_data['title'],
                story=cleaned_data['story'],
                request_id=request_id
            )
            
            # ===== STEP 5: Log success =====
            StoryLogger.log_submission_success(
                story_id=story.id,
                author_id=author.id,
                email=email,
                title=story.title,
                request_id=request_id
            )
            
            # ===== STEP 6: Calculate duration and log workflow summary =====
            duration_ms = (time.time() - start_time) * 1000
            LogSummary.submission_workflow(
                status="SUCCESS",
                story_id=story.id,
                author_id=author.id,
                email=email,
                title=story.title,
                duration_ms=duration_ms,
                request_id=request_id
            )
            
            # ===== STEP 7: Return result =====
            return {
                'story_id': str(story.id),
                'author_id': str(author.id),
                'status': story.status,
                'title': story.title,
                'created_at': story.created_at.isoformat() + "Z",
                'updated_at': story.updated_at.isoformat() + "Z"
            }
            
        except (ValidationFailedError, InvalidAuthorError, InvalidStoryError, DatabaseError):
            # Already logged, just re-raise
            duration_ms = (time.time() - start_time) * 1000
            LogSummary.submission_workflow(
                status="FAILED",
                email=email,
                duration_ms=duration_ms,
                error_code="VALIDATION_ERROR",
                error_message="Submission failed validation",
                request_id=request_id
            )
            raise
        
        except Exception as e:
            # Unexpected error
            StoryLogger.log_error(
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                email=email,
                operation="STORY_SUBMISSION",
                request_id=request_id,
                exception=e
            )
            
            duration_ms = (time.time() - start_time) * 1000
            LogSummary.submission_workflow(
                status="ERROR",
                email=email,
                duration_ms=duration_ms,
                error_code="UNEXPECTED_ERROR",
                error_message=str(e),
                request_id=request_id
            )
            
            raise DatabaseError(
                message="An unexpected error occurred during submission",
                operation="STORY_SUBMISSION"
            )
    
    @staticmethod
    def _get_or_create_author(email, first_name, last_name, phone, request_id=None):
        """
        Get existing author or create new one.
        
        Args:
            email (str): Author email (unique)
            first_name (str): Author first name
            last_name (str): Author last name
            phone (str): Author phone
            request_id (str): Unique request ID
        
        Returns:
            tuple: (Author instance, is_new: bool)
                - is_new=True if newly created
                - is_new=False if existing author reused
        
        Raises:
            InvalidAuthorError: If author creation fails
        """
        try:
            with transaction.atomic():
                author, created = Author.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'phone': phone
                    }
                )
                
                if created:
                    # New author created
                    StoryLogger.log_author_created(
                        author_id=author.id,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        request_id=request_id
                    )
                else:
                    # Existing author reused
                    StoryLogger.log_author_reused(
                        author_id=author.id,
                        email=email,
                        request_id=request_id
                    )
                
                return author, created
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="GET_OR_CREATE_AUTHOR",
                error_message=str(e),
                email=email,
                request_id=request_id,
                exception=e
            )
            raise InvalidAuthorError(
                message="Failed to get or create author",
                field="email",
                details={"email": email, "error": str(e)}
            )
    
    @staticmethod
    def _create_story(author, title, story, request_id=None):
        """
        Create story linked to author.
        
        Args:
            author (Author): Author instance
            title (str): Story title
            story (str): Story content
            request_id (str): Unique request ID
        
        Returns:
            Story: Created story instance
        
        Raises:
            InvalidStoryError: If story creation fails
        """
        try:
            with transaction.atomic():
                story_obj = Story.objects.create(
                    author=author,
                    title=title,
                    story=story,
                    status='pending'  # Default status
                )
                
                StoryLogger.log_story_created(
                    story_id=story_obj.id,
                    author_id=author.id,
                    title=title,
                    email=author.email,
                    request_id=request_id
                )
                
                return story_obj
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="CREATE_STORY",
                error_message=str(e),
                email=author.email,
                request_id=request_id,
                exception=e
            )
            raise InvalidStoryError(
                message="Failed to create story",
                field="story",
                details={"title": title, "error": str(e)}
            )


class StoryRetrievalService:
    """
    Handles story retrieval for admin dashboard and user views.
    """
    
    @staticmethod
    def get_story_by_id(story_id, request_id=None):
        """
        Retrieve a single story by ID.
        
        Args:
            story_id (UUID): Story ID to retrieve
            request_id (str): Unique request ID
        
        Returns:
            Story: Story instance with related author
        
        Raises:
            StoryNotFoundError: If story doesn't exist
        """
        try:
            story = Story.objects.select_related('author').get(id=story_id)
            return story
        
        except Story.DoesNotExist:
            StoryLogger.log_error(
                error_code="STORY_NOT_FOUND",
                error_message=f"Story with ID {story_id} not found",
                operation="GET_STORY",
                request_id=request_id
            )
            raise StoryNotFoundError(story_id=story_id)
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="GET_STORY",
                error_message=str(e),
                request_id=request_id,
                exception=e
            )
            raise DatabaseError(
                message="Failed to retrieve story",
                operation="GET_STORY"
            )
    
    @staticmethod
    def get_user_stories(author_id, request_id=None):
        """
        Retrieve all stories for a specific user (author).
        
        Args:
            author_id (UUID): Author ID to get stories for
            request_id (str): Unique request ID
        
        Returns:
            QuerySet: Stories for this author, ordered by created_at desc
        
        Raises:
            AuthorNotFoundError: If author doesn't exist
        """
        try:
            # Verify author exists
            author = Author.objects.get(id=author_id)
            
            # Get stories
            stories = Story.objects.filter(author=author).order_by('-created_at')
            return stories
        
        except Author.DoesNotExist:
            StoryLogger.log_error(
                error_code="AUTHOR_NOT_FOUND",
                error_message=f"Author with ID {author_id} not found",
                operation="GET_USER_STORIES",
                request_id=request_id
            )
            raise AuthorNotFoundError(author_id=author_id)
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="GET_USER_STORIES",
                error_message=str(e),
                request_id=request_id,
                exception=e
            )
            raise DatabaseError(
                message="Failed to retrieve user stories",
                operation="GET_USER_STORIES"
            )


class StoryModerationService:
    """
    Handles story moderation operations (for admin dashboard).
    """
    
    @staticmethod
    def update_story_status(story_id, new_status, request_id=None):
        """
        Update story status (pending → approved/denied).
        
        Args:
            story_id (UUID): Story ID to update
            new_status (str): New status (pending, approved, denied)
            request_id (str): Unique request ID
        
        Returns:
            Story: Updated story instance
        
        Raises:
            StoryNotFoundError: If story doesn't exist
            InvalidStoryError: If status is invalid
            DatabaseError: If update fails
        """
        valid_statuses = ['pending', 'approved', 'denied']
        
        if new_status not in valid_statuses:
            raise InvalidStoryError(
                message=f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}",
                field="status",
                details={"provided_status": new_status, "valid_statuses": valid_statuses}
            )
        
        try:
            story = Story.objects.get(id=story_id)
            old_status = story.status
            
            with transaction.atomic():
                story.status = new_status
                story.save(update_fields=['status', 'updated_at'])
                
                StoryLogger.log_story_updated(
                    story_id=story.id,
                    author_id=story.author.id,
                    old_status=old_status,
                    new_status=new_status,
                    request_id=request_id
                )
            
            return story
        
        except Story.DoesNotExist:
            raise StoryNotFoundError(story_id=story_id)
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="UPDATE_STORY_STATUS",
                error_message=str(e),
                request_id=request_id,
                exception=e
            )
            raise DatabaseError(
                message="Failed to update story status",
                operation="UPDATE_STORY_STATUS"
            )
    
    @staticmethod
    def delete_story(story_id, request_id=None):
        """
        Delete a story permanently.
        
        Args:
            story_id (UUID): Story ID to delete
            request_id (str): Unique request ID
        
        Returns:
            dict: Deletion confirmation
        
        Raises:
            StoryNotFoundError: If story doesn't exist
            DatabaseError: If deletion fails
        """
        try:
            story = Story.objects.get(id=story_id)
            title = story.title
            author_id = story.author.id
            
            with transaction.atomic():
                story.delete()
                
                StoryLogger.log_story_deleted(
                    story_id=story_id,
                    author_id=author_id,
                    title=title,
                    request_id=request_id
                )
            
            return {
                "message": f"Story '{title}' has been deleted successfully",
                "story_id": str(story_id)
            }
        
        except Story.DoesNotExist:
            raise StoryNotFoundError(story_id=story_id)
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="DELETE_STORY",
                error_message=str(e),
                request_id=request_id,
                exception=e
            )
            raise DatabaseError(
                message="Failed to delete story",
                operation="DELETE_STORY"
            )
    
    @staticmethod
    def get_pending_stories(request_id=None):
        """
        Get all pending stories for moderation queue.
        
        Args:
            request_id (str): Unique request ID
        
        Returns:
            QuerySet: Pending stories ordered by created_at (oldest first)
        """
        try:
            stories = Story.objects.filter(
                status='pending'
            ).select_related('author').order_by('created_at')
            
            return stories
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="GET_PENDING_STORIES",
                error_message=str(e),
                request_id=request_id,
                exception=e
            )
            raise DatabaseError(
                message="Failed to retrieve pending stories",
                operation="GET_PENDING_STORIES"
            )
    
    @staticmethod
    def get_approved_stories(request_id=None):
        """
        Get all approved stories (public).
        
        Args:
            request_id (str): Unique request ID
        
        Returns:
            QuerySet: Approved stories ordered by created_at (newest first)
        """
        try:
            stories = Story.objects.filter(
                status='approved'
            ).select_related('author').order_by('-created_at')
            
            return stories
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="GET_APPROVED_STORIES",
                error_message=str(e),
                request_id=request_id,
                exception=e
            )
            raise DatabaseError(
                message="Failed to retrieve approved stories",
                operation="GET_APPROVED_STORIES"
            )
    
    @staticmethod
    def bulk_update_stories(story_ids, new_status, request_id=None):
        """
        Update multiple stories at once.
        
        Args:
            story_ids (list): List of story UUIDs
            new_status (str): Status to apply to all
            request_id (str): Unique request ID
        
        Returns:
            dict: Update summary with count
        
        Raises:
            InvalidStoryError: If status is invalid
            DatabaseError: If bulk update fails
        """
        valid_statuses = ['approved', 'denied']
        
        if new_status not in valid_statuses:
            raise InvalidStoryError(
                message=f"Invalid status '{new_status}' for bulk update",
                field="status"
            )
        
        try:
            with transaction.atomic():
                updated_count = Story.objects.filter(
                    id__in=story_ids
                ).update(status=new_status)
            
            return {
                "message": f"Updated {updated_count} story(ies) to '{new_status}'",
                "updated_count": updated_count,
                "total_requested": len(story_ids)
            }
        
        except Exception as e:
            StoryLogger.log_database_error(
                operation="BULK_UPDATE_STORIES",
                error_message=str(e),
                request_id=request_id,
                exception=e
            )
            raise DatabaseError(
                message="Failed to bulk update stories",
                operation="BULK_UPDATE_STORIES"
            )