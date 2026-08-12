from django.shortcuts import render
from django.http import JsonResponse
from stories.models import Story
from .serializers import StorySubmissionSerializer
from rest_framework import generics

class StorySubmitView(generics.ListCreateAPIView):
    queryset=Story.objects.all()
    serializer_class=StorySubmissionSerializer

class StoryRetrieveTest(generics.RetrieveUpdateDestroyAPIView):
    queryset=Story.objects.all()
    serializer_class=StorySubmissionSerializer
    lookup_field='pk'