from django.contrib import admin
from .models import Story

admin.site.register(Story)
"""@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'status', 'submitted_at', 'ip_address']
    list_filter = ['status']
    search_fields = ['title', 'author_name']
"""