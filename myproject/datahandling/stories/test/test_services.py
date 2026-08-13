"""
stories/tests/test_services.py

Test suite for service layer.
Tests: StorySubmissionService, StoryRetrievalService, StoryModerationService
"""

from django.test import TestCase
from django.db import IntegrityError
from stories.models import Author, Story
from stories.services import (
    StorySubmissionService,
    StoryRetrievalService,
    StoryModerationService
)
from stories.exceptions import (
    ValidationFailedError,
    InvalidAuthorError,
    InvalidStoryError,
    StoryNotFoundError,
    AuthorNotFoundError,
    DatabaseError
)


class StorySubmissionServiceTests(TestCase):
    """Test story submission service"""
    
    def test_successful_story_submission(self):
        """Successful submission should create author and story"""
        data = {
            'email': 'john@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-1234',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        result = StorySubmissionService.submit_story(data)
        
        # Check result
        self.assertIn('story_id', result)
        self.assertIn('author_id', result)
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['title'], 'My Story')
        
        # Check author created
        author = Author.objects.get(email='john@gmail.com')
        self.assertEqual(author.first_name, 'John')
        self.assertEqual(author.last_name, 'Doe')
        
        # Check story created
        story = Story.objects.get(id=result['story_id'])
        self.assertEqual(story.author.id, author.id)
        self.assertEqual(story.title, 'My Story')
    
    def test_reuse_existing_author(self):
        """Submission with existing email should reuse author"""
        # Create first author
        author1 = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
        # Submit story with same email
        data = {
            'email': 'john@gmail.com',
            'first_name': 'Different',
            'last_name': 'Name',
            'title': 'Second Story',
            'story': 'This is a second story with at least 20 characters.'
        }
        
        result = StorySubmissionService.submit_story(data)
        
        # Check that same author is used
        story = Story.objects.get(id=result['story_id'])
        self.assertEqual(story.author.id, author1.id)
        self.assertEqual(story.author.first_name, 'John')  # Original name kept
        
        # Check only one author exists
        self.assertEqual(Author.objects.filter(email='john@gmail.com').count(), 1)
    
    def test_validation_failure_raises_error(self):
        """Invalid data should raise ValidationFailedError"""
        data = {
            'email': 'invalid',  # Invalid email
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        with self.assertRaises(ValidationFailedError) as cm:
            StorySubmissionService.submit_story(data)
        
        self.assertIn('email', cm.exception.details['field_errors'])
    
    def test_multiple_validation_errors(self):
        """Multiple errors should all be reported"""
        data = {
            'email': 'invalid',  # Invalid
            'first_name': 'A',  # Too short
            'last_name': 'Doe',
            'title': 'Bad',  # Too short
            'story': 'Short'  # Too short
        }
        
        with self.assertRaises(ValidationFailedError) as cm:
            StorySubmissionService.submit_story(data)
        
        errors = cm.exception.details['field_errors']
        self.assertGreater(len(errors), 1)
    
    def test_submission_with_request_id(self):
        """Submission with request_id should be tracked"""
        data = {
            'email': 'john@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        request_id = 'test-request-123'
        result = StorySubmissionService.submit_story(data, request_id=request_id)
        
        # Should complete successfully
        self.assertIn('story_id', result)
    
    def test_get_or_create_author(self):
        """_get_or_create_author should create or get author"""
        # Test create
        author1, created1 = StorySubmissionService._get_or_create_author(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe',
            phone='555-1234'
        )
        self.assertTrue(created1)
        self.assertEqual(author1.email, 'john@gmail.com')
        
        # Test get
        author2, created2 = StorySubmissionService._get_or_create_author(
            email='john@gmail.com',
            first_name='Different',
            last_name='Name',
            phone='999-9999'
        )
        self.assertFalse(created2)
        self.assertEqual(author2.id, author1.id)
        self.assertEqual(author2.first_name, 'John')  # Original kept
    
    def test_create_story(self):
        """_create_story should create story linked to author"""
        author = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
        story = StorySubmissionService._create_story(
            author=author,
            title='My Story',
            story='This is a story with at least 20 characters.'
        )
        
        self.assertEqual(story.author.id, author.id)
        self.assertEqual(story.title, 'My Story')
        self.assertEqual(story.status, 'pending')


class StoryRetrievalServiceTests(TestCase):
    """Test story retrieval service"""
    
    def setUp(self):
        """Set up test data"""
        # Create author
        self.author = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
        # Create stories
        self.story1 = Story.objects.create(
            author=self.author,
            title='Story 1',
            story='This is story 1 with at least 20 characters here.',
            status='pending'
        )
        self.story2 = Story.objects.create(
            author=self.author,
            title='Story 2',
            story='This is story 2 with at least 20 characters here.',
            status='approved'
        )
    
    def test_get_story_by_id(self):
        """get_story_by_id should retrieve story"""
        story = StoryRetrievalService.get_story_by_id(self.story1.id)
        
        self.assertEqual(story.id, self.story1.id)
        self.assertEqual(story.title, 'Story 1')
        self.assertEqual(story.author.id, self.author.id)
    
    def test_get_story_not_found(self):
        """get_story_by_id with invalid id should raise error"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(StoryNotFoundError):
            StoryRetrievalService.get_story_by_id(fake_uuid)
    
    def test_get_user_stories(self):
        """get_user_stories should return all user's stories"""
        stories = StoryRetrievalService.get_user_stories(self.author.id)
        
        self.assertEqual(stories.count(), 2)
        story_ids = [s.id for s in stories]
        self.assertIn(self.story1.id, story_ids)
        self.assertIn(self.story2.id, story_ids)
    
    def test_get_user_stories_ordered_newest_first(self):
        """Stories should be ordered by created_at descending"""
        stories = list(StoryRetrievalService.get_user_stories(self.author.id))
        
        # Newest first
        self.assertEqual(stories[0].id, self.story2.id)  # Created last
        self.assertEqual(stories[1].id, self.story1.id)  # Created first
    
    def test_get_user_stories_author_not_found(self):
        """get_user_stories with invalid author should raise error"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(AuthorNotFoundError):
            StoryRetrievalService.get_user_stories(fake_uuid)
    
    def test_get_user_stories_empty(self):
        """get_user_stories should return empty if no stories"""
        new_author = Author.objects.create(
            email='empty@gmail.com',
            first_name='Empty',
            last_name='Author'
        )
        
        stories = StoryRetrievalService.get_user_stories(new_author.id)
        self.assertEqual(stories.count(), 0)


class StoryModerationServiceTests(TestCase):
    """Test story moderation service"""
    
    def setUp(self):
        """Set up test data"""
        self.author = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
        self.story = Story.objects.create(
            author=self.author,
            title='Pending Story',
            story='This is a story with at least 20 characters here.',
            status='pending'
        )
    
    def test_update_story_status_pending_to_approved(self):
        """Update status from pending to approved"""
        story = StoryModerationService.update_story_status(
            story_id=self.story.id,
            new_status='approved'
        )
        
        self.assertEqual(story.status, 'approved')
        
        # Verify in database
        story_from_db = Story.objects.get(id=self.story.id)
        self.assertEqual(story_from_db.status, 'approved')
    
    def test_update_story_status_to_denied(self):
        """Update status to denied"""
        story = StoryModerationService.update_story_status(
            story_id=self.story.id,
            new_status='denied'
        )
        
        self.assertEqual(story.status, 'denied')
    
    def test_update_story_status_invalid_status(self):
        """Invalid status should raise error"""
        with self.assertRaises(InvalidStoryError):
            StoryModerationService.update_story_status(
                story_id=self.story.id,
                new_status='invalid'
            )
    
    def test_update_story_status_not_found(self):
        """Update non-existent story should raise error"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(StoryNotFoundError):
            StoryModerationService.update_story_status(
                story_id=fake_uuid,
                new_status='approved'
            )
    
    def test_delete_story(self):
        """Delete story should remove from database"""
        story_id = self.story.id
        story_title = self.story.title
        
        result = StoryModerationService.delete_story(story_id)
        
        # Check result
        self.assertIn('message', result)
        self.assertIn(story_title, result['message'])
        
        # Verify deleted from database
        with self.assertRaises(Story.DoesNotExist):
            Story.objects.get(id=story_id)
    
    def test_delete_story_not_found(self):
        """Delete non-existent story should raise error"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(StoryNotFoundError):
            StoryModerationService.delete_story(fake_uuid)
    
    def test_get_pending_stories(self):
        """get_pending_stories should return only pending stories"""
        # Create approved story
        Story.objects.create(
            author=self.author,
            title='Approved Story',
            story='This is a story with at least 20 characters here.',
            status='approved'
        )
        
        pending_stories = StoryModerationService.get_pending_stories()
        
        self.assertEqual(pending_stories.count(), 1)
        self.assertEqual(pending_stories.first().id, self.story.id)
    
    def test_get_approved_stories(self):
        """get_approved_stories should return only approved stories"""
        # Create approved story
        approved = Story.objects.create(
            author=self.author,
            title='Approved Story',
            story='This is a story with at least 20 characters here.',
            status='approved'
        )
        
        approved_stories = StoryModerationService.get_approved_stories()
        
        self.assertEqual(approved_stories.count(), 1)
        self.assertEqual(approved_stories.first().id, approved.id)
    
    def test_approved_stories_newest_first(self):
        """Approved stories should be ordered newest first"""
        story1 = Story.objects.create(
            author=self.author,
            title='Old Story',
            story='This is a story with at least 20 characters here.',
            status='approved'
        )
        story2 = Story.objects.create(
            author=self.author,
            title='New Story',
            story='This is a story with at least 20 characters here.',
            status='approved'
        )
        
        stories = list(StoryModerationService.get_approved_stories())
        
        # Newest first
        self.assertEqual(stories[0].id, story2.id)
        self.assertEqual(stories[1].id, story1.id)
    
    def test_bulk_update_stories(self):
        """Bulk update multiple stories"""
        story1 = self.story
        story2 = Story.objects.create(
            author=self.author,
            title='Story 2',
            story='This is a story with at least 20 characters here.',
            status='pending'
        )
        
        result = StoryModerationService.bulk_update_stories(
            story_ids=[story1.id, story2.id],
            new_status='approved'
        )
        
        self.assertEqual(result['updated_count'], 2)
        
        # Verify updated
        self.assertEqual(Story.objects.get(id=story1.id).status, 'approved')
        self.assertEqual(Story.objects.get(id=story2.id).status, 'approved')
    
    def test_bulk_update_invalid_status(self):
        """Bulk update with invalid status should raise error"""
        with self.assertRaises(InvalidStoryError):
            StoryModerationService.bulk_update_stories(
                story_ids=[self.story.id],
                new_status='invalid'
            )
    
    def test_bulk_update_empty_list(self):
        """Bulk update with empty list should work"""
        result = StoryModerationService.bulk_update_stories(
            story_ids=[],
            new_status='approved'
        )
        
        self.assertEqual(result['updated_count'], 0)