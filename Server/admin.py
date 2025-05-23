# Server/admin.py
from django.contrib import admin
from .models import FileHistory

@admin.register(FileHistory)
class FileHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'upload_date']
    list_filter = ['upload_date', 'user']
    search_fields = ['title', 'original_content', 'modified_content']