# Server/admin.py
from django.contrib import admin
from .models import OriginalData
from .models import UploadedFile

try:
    admin.site.unregister(OriginalData)  # 기존에 등록된 모델을 제거합니다.
except admin.sites.NotRegistered:
    pass

class OriginalDataAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'upload_file', 'original_text', 'processed_data', 'p_status', 'data_type', 'upload_date']

admin.site.register(OriginalData, OriginalDataAdmin)

admin.site.register(UploadedFile)