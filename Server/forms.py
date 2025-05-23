# Server/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile  # Profile 모델 import

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile  # Profile 모델 기반으로 폼 생성
        fields = ['image']  # 사용자에게 보일 필드 (image)