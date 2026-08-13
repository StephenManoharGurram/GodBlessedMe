"""
stories/exceptions.py

Custom exception classes for story submission flow.
Provides structured error handling with meaningful error codes and messages.
"""


class StorySubmissionError(Exception):
    """
    Base exception for all story submission errors.
    All other exceptions inherit from this.
    """
    
    def __init__(self, message, error_code=None, field=None, details=None):
        """
        Args:
            message (str): Human-readable error message
            error_code (str): Machine-readable error code (e.g., "INVALID_EMAIL")
            field (str): Field name where error occurred (e.g., "email")
            details (dict): Additional context information
        """
        self.message = message
        self.error_code = error_code or "SUBMISSION_ERROR"
        self.field = field
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self):
        """
        Convert exception to dictionary format for API response.
        
        Returns:
            dict: Structured error response
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "field": self.field,
            "details": self.details
        }


class InvalidAuthorError(StorySubmissionError):
    """
    Raised when author data is invalid (email, name, phone validation fails).
    """
    
    def __init__(self, message, field=None, details=None):
        super().__init__(
            message=message,
            error_code="INVALID_AUTHOR",
            field=field,
            details=details
        )


class InvalidStoryError(StorySubmissionError):
    """
    Raised when story data is invalid (title, content validation fails).
    """
    
    def __init__(self, message, field=None, details=None):
        super().__init__(
            message=message,
            error_code="INVALID_STORY",
            field=field,
            details=details
        )


class DuplicateAuthorError(StorySubmissionError):
    """
    Raised when an author with the same email already exists.
    This is NOT an error - we reuse the author.
    But we raise it to track that we're reusing an author.
    """
    
    def __init__(self, email, author_id, details=None):
        super().__init__(
            message=f"Author with email '{email}' already exists. Reusing author.",
            error_code="AUTHOR_REUSED",
            field="email",
            details={
                "email": email,
                "author_id": str(author_id),
                **(details or {})
            }
        )


class StoryNotFoundError(StorySubmissionError):
    """
    Raised when a story doesn't exist (used in dashboard/detail views).
    """
    
    def __init__(self, story_id, details=None):
        super().__init__(
            message=f"Story with ID '{story_id}' not found.",
            error_code="STORY_NOT_FOUND",
            details={
                "story_id": str(story_id),
                **(details or {})
            }
        )


class AuthorNotFoundError(StorySubmissionError):
    """
    Raised when an author doesn't exist.
    """
    
    def __init__(self, author_id, details=None):
        super().__init__(
            message=f"Author with ID '{author_id}' not found.",
            error_code="AUTHOR_NOT_FOUND",
            details={
                "author_id": str(author_id),
                **(details or {})
            }
        )


class DatabaseError(StorySubmissionError):
    """
    Raised when database operations fail (create, update, delete).
    """
    
    def __init__(self, message, operation=None, details=None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={
                "operation": operation,
                **(details or {})
            }
        )


class ValidationFailedError(StorySubmissionError):
    """
    Raised when validation fails with multiple field errors.
    """
    
    def __init__(self, field_errors, details=None):
        """
        Args:
            field_errors (dict): Dictionary of field names to error lists
                Example: {"email": ["Invalid email"], "title": ["Too short"]}
            details (dict): Additional context
        """
        error_count = len(field_errors)
        super().__init__(
            message=f"Validation failed for {error_count} field(s)",
            error_code="VALIDATION_FAILED",
            details={
                "field_errors": field_errors,
                "error_count": error_count,
                **(details or {})
            }
        )
    
    def to_dict(self):
        """
        Convert to dict with field_errors in the response.
        
        Returns:
            dict: Structured error with field-level errors
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "field_errors": self.details.get("field_errors", {}),
            "error_count": self.details.get("error_count", 0)
        }


class RateLimitError(StorySubmissionError):
    """
    Raised when rate limit is exceeded (backend rate limiting).
    """
    
    def __init__(self, retry_after=None, details=None):
        super().__init__(
            message="Too many requests. Please try again later.",
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "retry_after": retry_after,
                **(details or {})
            }
        )


class UnauthorizedError(StorySubmissionError):
    """
    Raised when user is not authorized to perform action.
    """
    
    def __init__(self, message="Unauthorized", details=None):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            details=details or {}
        )