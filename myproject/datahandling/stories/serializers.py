
"""
stories/serializers.py

DRF Serializers for story submission and retrieval.
Integrates with validators, exceptions, and response handling.
"""

from rest_framework import serializers
from .models import Author, Story
from .validator import validate_story_submission, FieldValidator, ValidationError as ValidatorError
from .exceptions import ValidationFailedError, InvalidAuthorError, InvalidStoryError


class StorySubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for story submission from frontend.
    
    Input (write_only):
    - email: Author email
    - first_name: Author first name
    - last_name: Author last name
    - phone: Author phone (optional)
    - title: Story title
    - story: Story content
    
    Output (read_only):
    - id: Story UUID
    - author_id: Author UUID
    - status: Story status (pending/approved/denied)
    - created_at: When story was created
    - updated_at: When story was last updated
    """
    
    # Write-only fields (from frontend, not included in response)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True, max_length=100)
    last_name = serializers.CharField(write_only=True, max_length=100)
    phone = serializers.CharField(write_only=True, max_length=12, required=False, allow_blank=True)
    
    # Read-only fields (in response, not from frontend)
    author_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            # Read-only (in response)
            'id',
            'author_id',
            'status',
            'created_at',
            'updated_at',
            # Write-only (from frontend)
            'email',
            'first_name',
            'last_name',
            'phone',
            'title',
            'story'
        ]
        read_only_fields = ['id', 'author_id', 'status', 'created_at', 'updated_at']
    
    def get_author_id(self, obj):
        """
        Extract author_id from the story's author FK.
        
        Args:
            obj (Story): Story instance
            
        Returns:
            str: Author UUID
        """
        return str(obj.author.id)
    
    def validate(self, data):
        """
        Comprehensive validation using validators.py
        Validates all fields together.
        
        Args:
            data (dict): Data to validate
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationFailedError: If any field fails validation
        """
        try:
            # Use the comprehensive validator from validators.py
            cleaned_data = validate_story_submission(data)
            return cleaned_data
        except dict as field_errors:
            # Validator returns dict of field errors
            raise ValidationFailedError(field_errors)
        except ValidatorError as e:
            # Single validator error
            raise ValidationFailedError({e.field or "unknown": [e.message]})
    
    def create(self, validated_data):
        """
        Create story with author (get_or_create).
        
        The flow:
        1. Extract author fields from validated_data
        2. Get or create Author by email
        3. Create Story linked to Author
        4. Return story instance
        
        Args:
            validated_data (dict): Validated submission data
            
        Returns:
            Story: Created story instance with author
            
        Raises:
            InvalidAuthorError: If author creation fails
            InvalidStoryError: If story creation fails
        """
        try:
            # 1. Extract author data
            email = validated_data.pop('email')
            first_name = validated_data.pop('first_name')
            last_name = validated_data.pop('last_name')
            phone = validated_data.pop('phone', '')
            
            # 2. Get or create author
            author, created = Author.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone
                }
            )
            
            # 3. Create story linked to author
            story = Story.objects.create(
                author=author,
                **validated_data
            )
            
            return story
            
        except Author.DoesNotExist as e:
            raise InvalidAuthorError(
                message="Failed to get or create author",
                field="email",
                details={"email": email}
            )
        except Exception as e:
            raise InvalidStoryError(
                message=f"Failed to create story: {str(e)}",
                details={"exception": str(type(e).__name__)}
            )


class StoryDisplaySerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving user's stories (from frontend).
    Shows story details with author name.
    
    Used by: UserStoryListAPIView
    """
    author_name = serializers.SerializerMethodField()
    author_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            'id',
            'author_id',
            'author_name',
            'title',
            'story',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
    
    def get_author_name(self, obj):
        """Get full name of author"""
        return f"{obj.author.first_name} {obj.author.last_name}"
    
    def get_author_id(self, obj):
        """Get author UUID"""
        return str(obj.author.id)


# ============================================================================
# Dashboard Serializers (for admin moderation views)
# ============================================================================

class AuthorDetailSerializer(serializers.ModelSerializer):
    """
    Serialize author information for admin/dashboard views.
    
    Shows: id, first_name, last_name, email, phone, created_at
    """
    class Meta:
        model = Author
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class DashboardStoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for admin list view - minimal fields for moderation queue.
    
    Shows: id, title, author_name, author_email, status, created_at, updated_at
    Used for the moderation queue list.
    """
    author_name = serializers.SerializerMethodField()
    author_email = serializers.SerializerMethodField()
    author_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            'id',
            'author_id',
            'title',
            'author_name',
            'author_email',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
    
    def get_author_name(self, obj):
        """Full name of author"""
        return f"{obj.author.first_name} {obj.author.last_name}"
    
    def get_author_email(self, obj):
        """Email of author"""
        return obj.author.email
    
    def get_author_id(self, obj):
        """UUID of author"""
        return str(obj.author.id)


class DashboardStoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for admin detail view - full story content + author details.
    
    Shows: id, title, story content, author (nested), status, timestamps
    Used when admin clicks on a story to see full details.
    """
    author = AuthorDetailSerializer(read_only=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            'id',
            'title',
            'story',
            'author',
            'author_name',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
    
    def get_author_name(self, obj):
        """Full name of author"""
        return f"{obj.author.first_name} {obj.author.last_name}"


class StoryStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating story status (admin only).
    
    Input:
    - status: One of (pending, approved, denied)
    
    Used by: Admin to change story moderation status
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    
    def validate_status(self, value):
        """
        Validate status value.
        
        Args:
            value (str): Status value
            
        Returns:
            str: Validated status
        """
        valid_statuses = ['pending', 'approved', 'denied']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status '{value}'. Must be one of: {', '.join(valid_statuses)}"
            )
        return value


class BulkStoryStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating multiple stories at once.
    
    Input:
    - story_ids: List of story UUIDs
    - status: Status to apply to all
    
    Used by: Admin bulk moderation operations
    """
    story_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False
    )
    status = serializers.ChoiceField(
        choices=[
            ('approved', 'Approved'),
            ('denied', 'Denied'),
        ]
    )
    
    def validate(self, data):
        """
        Validate bulk operation.
        
        Args:
            data (dict): Bulk operation data
            
        Returns:
            dict: Validated data
        """
        if len(data.get('story_ids', [])) == 0:
            raise serializers.ValidationError(
                "At least one story ID is required"
            )
        
        if len(data.get('story_ids', [])) > 100:
            raise serializers.ValidationError(
                "Cannot update more than 100 stories at once"
            )
        
        return data