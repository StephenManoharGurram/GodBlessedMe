"""
Dashboard Services - Business logic for story operations
These functions are called by API app views only.
No endpoints are exposed directly from this module.
"""

from django.db.models import Q
from stories.models import Story
from rest_framework.exceptions import NotFound, ValidationError


class StoryService:
    """Service class for story operations"""

    @staticmethod
    def fetch_all_stories(filters=None, ordering='-created_at'):
        """
        Fetch all stories with optional filters
        
        Args:
            filters (dict): Optional filters with keys:
                - status: Filter by story status (pending, approved, denied)
                - search: Search in title or author name
                
            ordering (str): Field to order by (default: -created_at)
        
        Returns:
            QuerySet: Optimized queryset with select_related author
        """
        queryset = Story.objects.select_related('author').order_by(ordering)
        
        if filters:
            # Filter by status if provided
            status = filters.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            # Search functionality
            search = filters.get('search')
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(author__first_name__icontains=search) |
                    Q(author__last_name__icontains=search)
                )
        
        return queryset

    @staticmethod
    def get_story_detail(story_id):
        """
        Fetch a single story by ID
        
        Args:
            story_id (UUID): Story ID to fetch
        
        Returns:
            Story: Story object with related author
        
        Raises:
            NotFound: If story doesn't exist
        """
        try:
            return Story.objects.select_related('author').get(id=story_id)
        except Story.DoesNotExist:
            raise NotFound(f"Story with ID {story_id} not found.")

    @staticmethod
    def update_story_status(story_id, new_status):
        """
        Update the status of a story
        
        Args:
            story_id (UUID): Story ID to update
            new_status (str): New status value (pending, approved, denied)
        
        Returns:
            Story: Updated story object
        
        Raises:
            NotFound: If story doesn't exist
            ValidationError: If status is invalid
        """
        valid_statuses = ['pending', 'approved', 'denied']
        
        if new_status not in valid_statuses:
            raise ValidationError(
                f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"
            )
        
        story = StoryService.get_story_detail(story_id)
        story.status = new_status
        story.save(update_fields=['status', 'updated_at'])
        
        return story

    @staticmethod
    def delete_story(story_id):
        """
        Delete a story by ID
        
        Args:
            story_id (UUID): Story ID to delete
        
        Returns:
            dict: Confirmation message
        
        Raises:
            NotFound: If story doesn't exist
        """
        story = StoryService.get_story_detail(story_id)
        story.delete()
        
        return {
            "message": f"Story '{story.title}' has been deleted.",
            "story_id": str(story_id)
        }