from django.urls import path
from .views import StoryCreateAPIView, UserStoryListAPIView

urlpatterns = [
    # API endpoint for Next.js to submit a new story
    path('submit/', StoryCreateAPIView.as_view(), name='story-submit'),
    
    # API endpoint to fetch all stories belonging to a specific user
    path('user/<uuid:author_id>/', UserStoryListAPIView.as_view(), name='user-stories'),
]