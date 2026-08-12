from django.urls import path, include

urlpatterns=[
    path('stories/',include('stories.urls')),
    path('dashboard/', include('dashboard.urls')),
]