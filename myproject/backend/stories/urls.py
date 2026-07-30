from django.urls import path
from .views import (
    PublicStoryListView,
    PublicStorySubmitView,
    AdminStoryListView,
    AdminStoryDetailView,
)

urlpatterns = [
    path("stories/", PublicStoryListView.as_view(), name="public-story-list"),
    path("stories/submit/", PublicStorySubmitView.as_view(), name="public-story-submit"),
    path("stories/admin/", AdminStoryListView.as_view(), name="admin-story-list"),
    path("stories/admin/<int:pk>/", AdminStoryDetailView.as_view(), name="admin-story-detail"),
]