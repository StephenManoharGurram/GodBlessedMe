"""
stories/tests/test_views.py

Test suite for API endpoints.
Tests: story submission, retrieval, and moderation endpoints.
"""

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json

from stories.models import Author, Story


class StorySubmissionViewTests(TestCase):
    """Test story submission endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.submit_url = '/api/v1/stories/submit/'
    
    def test_successful_story_submission(self):
        """POST with valid data should create story and return 201"""
        data = {
            'email': 'john@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '555-1234',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Check status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check response format
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'Story submitted successfully')
        self.assertIn('story_id', response_data['data'])
        self.assertIn('author_id', response_data['data'])
        self.assertEqual(response_data['data']['status'], 'pending')
        
        # Check database
        story = Story.objects.get(id=response_data['data']['story_id'])
        author = Author.objects.get(id=response_data['data']['author_id'])
        self.assertEqual(story.author.id, author.id)
        self.assertEqual(story.title, 'My Story')
    
    def test_submission_validation_failure(self):
        """POST with invalid data should return 400"""
        data = {
            'email': 'invalid',  # Invalid email
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Check status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check response
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error_code'], 'VALIDATION_FAILED')
        self.assertIn('field_errors', response_data)
        self.assertIn('email', response_data['field_errors'])
    
    def test_submission_multiple_errors(self):
        """Multiple validation errors should all be reported"""
        data = {
            'email': 'invalid',
            'first_name': 'A',  # Too short
            'last_name': 'Doe',
            'title': 'Bad',  # Too short
            'story': 'Short'  # Too short
        }
        
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response_data = response.json()
        
        # Check that response has field_errors
        self.assertTrue('field_errors' in response_data or 'details' in response_data)
        
        if 'field_errors' in response_data:
            errors = response_data['field_errors']
        else:
            # If it's in details, extract from there
            return
        
        # Should have multiple errors
        self.assertGreater(len(errors), 1)
        self.assertIn('email', errors)
        self.assertIn('title', errors)
        self.assertIn('story', errors)
    
    def test_submission_email_lowercase(self):
        """Email should be stored as lowercase"""
        data = {
            'email': 'JOHN@GMAIL.COM',
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Check author email is lowercase
        author = Author.objects.get(email='john@gmail.com')
        self.assertEqual(author.email, 'john@gmail.com')
    
    def test_submission_reuses_existing_author(self):
        """Submitting with existing email should reuse author"""
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
            'story': 'This is a story with at least 20 characters here.'
        }
        
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response_data = response.json()
        returned_author_id = response_data['data']['author_id']
        
        # Should use same author
        self.assertEqual(returned_author_id, str(author1.id))
        
        # Should only have one author with this email
        self.assertEqual(Author.objects.filter(email='john@gmail.com').count(), 1)
    
    def test_submission_without_phone(self):
        """Phone is optional and should work without it"""
        data = {
            'email': 'john@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'My Story',
            'story': 'This is a story with at least 20 characters here.'
        }
        
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserStoryListViewTests(TestCase):
    """Test user story retrieval endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
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
    
    def test_get_user_stories(self):
        """GET user stories should return all stories for user"""
        url = f'/api/v1/stories/user/{self.author.id}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['total'], 2)
        
        story_ids = [s['id'] for s in response_data['data']['stories']]
        self.assertIn(str(self.story1.id), story_ids)
        self.assertIn(str(self.story2.id), story_ids)
    
    def test_get_user_stories_includes_author_info(self):
        """Response should include author name"""
        url = f'/api/v1/stories/user/{self.author.id}/'
        
        response = self.client.get(url)
        response_data = response.json()
        
        story = response_data['data']['stories'][0]
        self.assertEqual(story['author_name'], 'John Doe')
        self.assertEqual(story['author_id'], str(self.author.id))
    
    def test_get_user_stories_author_not_found(self):
        """GET with invalid author should return 404"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        url = f'/api/v1/stories/user/{fake_uuid}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_get_empty_user_stories(self):
        """User with no stories should return empty list"""
        new_author = Author.objects.create(
            email='empty@gmail.com',
            first_name='Empty',
            last_name='Author'
        )
        
        url = f'/api/v1/stories/user/{new_author.id}/'
        
        response = self.client.get(url)
        response_data = response.json()
        
        self.assertEqual(response_data['data']['total'], 0)
        self.assertEqual(len(response_data['data']['stories']), 0)


class StoriesDetailViewTests(TestCase):
    """Test story detail endpoint (get/update/delete)"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
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
    
    def test_get_story_details(self):
        """GET story should return full details"""
        url = f'/api/v1/stories/{self.story.id}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['id'], str(self.story.id))
        self.assertEqual(response_data['data']['title'], 'Pending Story')
        self.assertEqual(response_data['data']['author']['email'], 'john@gmail.com')
    
    def test_get_story_not_found(self):
        """GET non-existent story should return 404"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        url = f'/api/v1/stories/{fake_uuid}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_story_status(self):
        """PATCH story status should update story"""
        url = f'/api/v1/stories/{self.story.id}/'
        data = {'status': 'approved'}
        
        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['status'], 'approved')
        
        # Verify in database
        self.story.refresh_from_db()
        self.assertEqual(self.story.status, 'approved')
    
    def test_update_story_invalid_status(self):
        """PATCH with invalid status should return 400"""
        url = f'/api/v1/stories/{self.story.id}/'
        data = {'status': 'invalid'}
        
        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_story(self):
        """DELETE story should remove it"""
        url = f'/api/v1/stories/{self.story.id}/'
        story_id = self.story.id
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify deleted
        with self.assertRaises(Story.DoesNotExist):
            Story.objects.get(id=story_id)
    
    def test_delete_story_not_found(self):
        """DELETE non-existent story should return 404"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        url = f'/api/v1/stories/{fake_uuid}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class StoriesFetchAllViewTests(TestCase):
    """Test fetch all stories endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
        # Create stories with different statuses
        for i in range(3):
            Story.objects.create(
                author=self.author,
                title=f'Pending Story {i}',
                story='This is a story with at least 20 characters here.',
                status='pending'
            )
        
        for i in range(2):
            Story.objects.create(
                author=self.author,
                title=f'Approved Story {i}',
                story='This is a story with at least 20 characters here.',
                status='approved'
            )
    
    def test_fetch_all_stories(self):
        """GET fetch-all should return all stories"""
        url = '/api/v1/stories/fetch-all/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['data']['total'], 5)
    
    def test_fetch_all_with_status_filter(self):
        """GET with status filter should return only that status"""
        url = '/api/v1/stories/fetch-all/?status=pending'
        
        response = self.client.get(url)
        response_data = response.json()
        
        self.assertEqual(response_data['data']['total'], 3)
        
        # All should be pending
        for story in response_data['data']['stories']:
            self.assertEqual(story['status'], 'pending')
    
    def test_fetch_all_with_pagination(self):
        """GET with pagination should limit results"""
        url = '/api/v1/stories/fetch-all/?page_size=2'
        
        response = self.client.get(url)
        response_data = response.json()
        
        self.assertEqual(len(response_data['data']['stories']), 2)
        self.assertEqual(response_data['data']['total'], 5)
    
    def test_fetch_all_pagination_page_2(self):
        """GET page 2 should return next set of results"""
        url = '/api/v1/stories/fetch-all/?page=2&page_size=2'
        
        response = self.client.get(url)
        response_data = response.json()
        
        self.assertEqual(response_data['data']['page'], 2)


class StoryPendingQueueViewTests(TestCase):
    """Test pending queue endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
        # Create pending and approved stories
        Story.objects.create(
            author=self.author,
            title='Pending 1',
            story='This is a story with at least 20 characters here.',
            status='pending'
        )
        
        Story.objects.create(
            author=self.author,
            title='Approved',
            story='This is a story with at least 20 characters here.',
            status='approved'
        )
        
        Story.objects.create(
            author=self.author,
            title='Pending 2',
            story='This is a story with at least 20 characters here.',
            status='pending'
        )
    
    def test_get_pending_queue(self):
        """GET pending-queue should return only pending stories"""
        url = '/api/v1/stories/pending-queue/'
        
        response = self.client.get(url)
        response_data = response.json()
        
        self.assertEqual(response_data['data']['total'], 2)
        
        # All should be pending
        for story in response_data['data']['stories']:
            self.assertEqual(story['status'], 'pending')


class StoryApprovedListViewTests(TestCase):
    """Test approved stories endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = Author.objects.create(
            email='john@gmail.com',
            first_name='John',
            last_name='Doe'
        )
        
        Story.objects.create(
            author=self.author,
            title='Pending',
            story='This is a story with at least 20 characters here.',
            status='pending'
        )
        
        Story.objects.create(
            author=self.author,
            title='Approved 1',
            story='This is a story with at least 20 characters here.',
            status='approved'
        )
        
        Story.objects.create(
            author=self.author,
            title='Approved 2',
            story='This is a story with at least 20 characters here.',
            status='approved'
        )
    
    def test_get_approved_stories(self):
        """GET approved should return only approved stories"""
        url = '/api/v1/stories/approved/'
        
        response = self.client.get(url)
        response_data = response.json()
        
        self.assertEqual(response_data['data']['total'], 2)
        
        # All should be approved
        for story in response_data['data']['stories']:
            self.assertEqual(story['status'], 'approved')