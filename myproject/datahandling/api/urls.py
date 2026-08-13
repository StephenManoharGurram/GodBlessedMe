from django.urls import path, include
from .views import StoriesFetchAllAPIView, StoriesDetailAPIView

urlpatterns=[
    path('stories/',include('stories.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('stories/fetch-all/', StoriesFetchAllAPIView.as_view(), name='stories-fetch-all'),
    path('stories/<uuid:story_id>/', StoriesDetailAPIView.as_view(), name='stories-detail'),
]
