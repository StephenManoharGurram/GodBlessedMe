"""
stories/urls.py

URL routing for story submission and retrieval endpoints.
All endpoints are nested under /api/v1/stories/
"""

from django.urls import path
from .views import (
    StoryCreateAPIView,
    UserStoryListAPIView,
    StoriesFetchAllAPIView,
    StoriesDetailAPIView,
    StoryPendingQueueAPIView,
    StoryApprovedListAPIView,
)

app_name = 'stories'

urlpatterns = [
    # =========================================================================
    # USER ENDPOINTS - Story Submission & Retrieval
    # =========================================================================
    
    # POST /api/v1/stories/submit/
    # Submit a new story
    path(
        'submit/',
        StoryCreateAPIView.as_view(),
        name='story-submit'
    ),
    
    # GET /api/v1/stories/user/<author_id>/
    # Retrieve all stories by a specific user
    path(
        'user/<uuid:author_id>/',
        UserStoryListAPIView.as_view(),
        name='user-stories'
    ),
    
    
    # =========================================================================
    # ADMIN ENDPOINTS - Dashboard & Moderation
    # =========================================================================
    
    # GET /api/v1/stories/fetch-all/
    # Retrieve all stories with optional filtering and pagination
    path(
        'fetch-all/',
        StoriesFetchAllAPIView.as_view(),
        name='stories-fetch-all'
    ),
    
    # GET /api/v1/stories/pending-queue/
    # Retrieve pending stories for admin moderation queue
    path(
        'pending-queue/',
        StoryPendingQueueAPIView.as_view(),
        name='stories-pending-queue'
    ),
    
    # GET /api/v1/stories/approved/
    # Retrieve approved (published) stories
    path(
        'approved/',
        StoryApprovedListAPIView.as_view(),
        name='stories-approved'
    ),
    
    # GET /api/v1/stories/<story_id>/
    # PATCH /api/v1/stories/<story_id>/
    # DELETE /api/v1/stories/<story_id>/
    # Retrieve, update, or delete a specific story
    path(
        '<uuid:story_id>/',
        StoriesDetailAPIView.as_view(),
        name='stories-detail'
    ),
]