"""
stories/logger.py

Centralized logging for story submission flow.
Logs: submissions, validation failures, errors, and operations.
Provides structured, traceable logs with timestamps and context.
"""

import logging
import json
from datetime import datetime
from django.conf import settings


# Get or create logger for stories app
logger = logging.getLogger('stories')


class LogContext:
    """
    Structured context for logging.
    Tracks user, request, and operation details.
    """
    
    def __init__(self, operation, request_id=None, ip_address=None):
        """
        Args:
            operation (str): Type of operation (e.g., 'STORY_SUBMISSION')
            request_id (str): Unique request identifier (optional)
            ip_address (str): Client IP address (optional)
        """
        self.operation = operation
        self.request_id = request_id
        self.ip_address = ip_address
        self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self):
        """Convert context to dictionary"""
        return {
            "operation": self.operation,
            "request_id": self.request_id,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp
        }


class StoryLogger:
    """
    Centralized logging for story operations.
    Tracks submissions, validations, errors, and database operations.
    """
    
    @staticmethod
    def log_submission_attempt(email, ip_address=None, request_id=None):
        """
        Log when a story submission is attempted.
        
        Args:
            email (str): Author email
            ip_address (str): Client IP address
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="SUBMISSION_ATTEMPT",
            request_id=request_id,
            ip_address=ip_address
        )
        
        log_data = {
            **context.to_dict(),
            "email": email,
            "status": "INITIATED"
        }
        
        logger.info(
            f"Story submission attempt | Email: {email}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_validation_success(email, title, request_id=None):
        """
        Log when validation passes.
        
        Args:
            email (str): Author email
            title (str): Story title
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="VALIDATION_SUCCESS",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "email": email,
            "title": title,
            "status": "PASSED"
        }
        
        logger.info(
            f"Validation passed | Email: {email}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_validation_failure(email, field_errors, request_id=None):
        """
        Log when validation fails.
        
        Args:
            email (str): Author email (if available)
            field_errors (dict): Fields that failed validation
                Example: {"email": ["Invalid format"], "title": ["Too short"]}
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="VALIDATION_FAILURE",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "email": email or "UNKNOWN",
            "failed_fields": list(field_errors.keys()),
            "error_count": len(field_errors),
            "field_details": field_errors,
            "status": "FAILED"
        }
        
        logger.warning(
            f"Validation failed for {len(field_errors)} field(s) | Email: {email}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_author_created(author_id, email, first_name, last_name, request_id=None):
        """
        Log when a new author is created.
        
        Args:
            author_id (UUID): Created author ID
            email (str): Author email
            first_name (str): Author first name
            last_name (str): Author last name
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="AUTHOR_CREATED",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "author_id": str(author_id),
            "email": email,
            "name": f"{first_name} {last_name}",
            "status": "CREATED"
        }
        
        logger.info(
            f"New author created | ID: {author_id} | Email: {email}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_author_reused(author_id, email, request_id=None):
        """
        Log when an existing author is reused.
        
        Args:
            author_id (UUID): Reused author ID
            email (str): Author email
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="AUTHOR_REUSED",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "author_id": str(author_id),
            "email": email,
            "status": "REUSED"
        }
        
        logger.info(
            f"Existing author reused | ID: {author_id} | Email: {email}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_story_created(story_id, author_id, title, email, request_id=None):
        """
        Log when a story is successfully created.
        
        Args:
            story_id (UUID): Created story ID
            author_id (UUID): Associated author ID
            title (str): Story title
            email (str): Author email
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="STORY_CREATED",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "story_id": str(story_id),
            "author_id": str(author_id),
            "title": title,
            "email": email,
            "status": "CREATED"
        }
        
        logger.info(
            f"Story created | Story ID: {story_id} | Author ID: {author_id}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_submission_success(story_id, author_id, email, title, request_id=None):
        """
        Log successful story submission (end-to-end).
        
        Args:
            story_id (UUID): Created story ID
            author_id (UUID): Associated author ID
            email (str): Author email
            title (str): Story title
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="SUBMISSION_SUCCESS",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "story_id": str(story_id),
            "author_id": str(author_id),
            "email": email,
            "title": title,
            "status": "SUCCESS"
        }
        
        logger.info(
            f"Story submission successful | Story ID: {story_id} | Email: {email}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_story_updated(story_id, author_id, old_status, new_status, request_id=None):
        """
        Log when a story status is updated.
        
        Args:
            story_id (UUID): Story ID
            author_id (UUID): Author ID
            old_status (str): Previous status
            new_status (str): New status
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="STORY_UPDATED",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "story_id": str(story_id),
            "author_id": str(author_id),
            "old_status": old_status,
            "new_status": new_status,
            "status": "UPDATED"
        }
        
        logger.info(
            f"Story updated | Story ID: {story_id} | Status: {old_status} → {new_status}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_story_deleted(story_id, author_id, title, request_id=None):
        """
        Log when a story is deleted.
        
        Args:
            story_id (UUID): Deleted story ID
            author_id (UUID): Author ID
            title (str): Story title
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="STORY_DELETED",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "story_id": str(story_id),
            "author_id": str(author_id),
            "title": title,
            "status": "DELETED"
        }
        
        logger.info(
            f"Story deleted | Story ID: {story_id} | Title: {title}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_error(error_code, error_message, email=None, operation=None, request_id=None, exception=None):
        """
        Log errors that occur during operations.
        
        Args:
            error_code (str): Error code (e.g., "DATABASE_ERROR")
            error_message (str): Error message
            email (str): Author email (if applicable)
            operation (str): Operation where error occurred
            request_id (str): Unique request ID
            exception (Exception): The actual exception object
        """
        context = LogContext(
            operation=operation or "ERROR",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "error_code": error_code,
            "error_message": error_message,
            "email": email or "UNKNOWN",
            "status": "ERROR"
        }
        
        if exception:
            log_data["exception_type"] = type(exception).__name__
            log_data["exception_detail"] = str(exception)
        
        logger.error(
            f"Error occurred | Code: {error_code} | Message: {error_message}",
            extra={"context": log_data},
            exc_info=exception is not None
        )
    
    @staticmethod
    def log_rate_limit_exceeded(ip_address, email=None, request_id=None):
        """
        Log when rate limit is exceeded.
        
        Args:
            ip_address (str): Client IP address
            email (str): Author email (if known)
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="RATE_LIMIT_EXCEEDED",
            request_id=request_id,
            ip_address=ip_address
        )
        
        log_data = {
            **context.to_dict(),
            "ip_address": ip_address,
            "email": email or "UNKNOWN",
            "status": "RATE_LIMITED"
        }
        
        logger.warning(
            f"Rate limit exceeded | IP: {ip_address}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_unauthorized_access(email, operation, request_id=None):
        """
        Log unauthorized access attempts.
        
        Args:
            email (str): User attempting access
            operation (str): Operation attempted
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="UNAUTHORIZED_ACCESS",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "email": email,
            "attempted_operation": operation,
            "status": "UNAUTHORIZED"
        }
        
        logger.warning(
            f"Unauthorized access attempt | Email: {email} | Operation: {operation}",
            extra={"context": log_data}
        )
    
    @staticmethod
    def log_database_error(operation, error_message, email=None, request_id=None, exception=None):
        """
        Log database operation errors.
        
        Args:
            operation (str): Database operation (CREATE, UPDATE, DELETE, etc.)
            error_message (str): Error message
            email (str): Related author email
            request_id (str): Unique request ID
            exception (Exception): The actual exception
        """
        context = LogContext(
            operation=f"DB_{operation}",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "db_operation": operation,
            "error_message": error_message,
            "email": email or "UNKNOWN",
            "status": "DB_ERROR"
        }
        
        if exception:
            log_data["exception_type"] = type(exception).__name__
            log_data["exception_detail"] = str(exception)
        
        logger.error(
            f"Database error | Operation: {operation} | Message: {error_message}",
            extra={"context": log_data},
            exc_info=exception is not None
        )


class LogSummary:
    """
    Creates summary logs for complete workflows.
    Useful for tracking end-to-end submission flow.
    """
    
    @staticmethod
    def submission_workflow(
        status,
        story_id=None,
        author_id=None,
        email=None,
        title=None,
        duration_ms=None,
        error_code=None,
        error_message=None,
        request_id=None
    ):
        """
        Log complete submission workflow summary.
        
        Args:
            status (str): Final status (SUCCESS, FAILED, ERROR)
            story_id (UUID): Story ID (if successful)
            author_id (UUID): Author ID
            email (str): Author email
            title (str): Story title
            duration_ms (float): How long the submission took (milliseconds)
            error_code (str): Error code (if failed)
            error_message (str): Error message (if failed)
            request_id (str): Unique request ID
        """
        context = LogContext(
            operation="SUBMISSION_WORKFLOW_SUMMARY",
            request_id=request_id
        )
        
        log_data = {
            **context.to_dict(),
            "final_status": status,
            "story_id": str(story_id) if story_id else None,
            "author_id": str(author_id) if author_id else None,
            "email": email,
            "title": title,
            "duration_ms": duration_ms,
            "error_code": error_code,
            "error_message": error_message
        }
        
        if status == "SUCCESS":
            logger.info(
                f"Submission workflow completed successfully | Email: {email}",
                extra={"context": log_data}
            )
        elif status == "FAILED":
            logger.warning(
                f"Submission workflow failed | Error: {error_code}",
                extra={"context": log_data}
            )
        else:
            logger.error(
                f"Submission workflow error | Error: {error_code}",
                extra={"context": log_data}
            )