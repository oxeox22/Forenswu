# Server/forms.py
from django import forms
from .models import OriginalData

class OriginalDataForm(forms.ModelForm):
    class Meta:
        model = OriginalData
        fields = ['user_id', 'upload_file', 'original_text', 'processed_data', 'p_status', 'data_type']  # 필요한 필드만 나열
