# Server/forms.py
from django import forms
from .models import OriginalData
from .models import Profile  # Profile 모델 import

class OriginalDataForm(forms.ModelForm):
    class Meta:
        model = OriginalData
        fields = ['user_id', 'upload_file', 'original_text', 'processed_data', 'p_status', 'data_type']  # 필요한 필드만 나열

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile  # Profile 모델 기반으로 폼 생성
        fields = ['image']  # 사용자에게 보일 필드 (image)