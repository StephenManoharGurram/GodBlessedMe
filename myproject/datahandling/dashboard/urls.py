from django.urls import path
from .views import DashboardStoryListView, DashboardStoryDetailView, StoryListView,DashboardActionReceiverAPIView

urlpatterns = [
    # GET request here retrieves the full list of stories
    #path('stories/', DashboardStoryListView.as_view(), name='dashboard-story-list'),
    # GET/PATCH/DELETE requests here operate on one specific story
    path('stories/<uuid:pk>/', DashboardStoryDetailView.as_view(), name='dashboard-story-detail'),
    path("stories/", StoryListView.as_view(), name="dashboard-story-list"),
     path("action/", DashboardActionReceiverAPIView.as_view(), name="dashboard-action"),
]