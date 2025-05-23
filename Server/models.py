from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.contrib.auth.models import User

# User 모델
class User(models.Model):
    user_id = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=[('admin', '관리자'), ('user', '일반 사용자')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    u_status = models.CharField(max_length=20, choices=[('active', '활성'), ('suspended', '정지')])

    def __str__(self):
        return self.username


# original_data 모델
class OriginalData(models.Model):
    user_id = models.CharField(max_length=100)  # 사용자 ID
    upload_file = models.FileField(upload_to='uploads/')  # 파일 저장 위치
    original_text = models.TextField(blank=True, null=True)  # 원본 텍스트
    processed_data = models.TextField(blank=True, null=True)  # 처리된 텍스트
    p_status = models.CharField(max_length=20, blank=True, null=True)  # 처리 상태
    data_type = models.CharField(max_length=50, blank=True, null=True)  # 데이터 유형
    upload_date = models.DateTimeField(auto_now_add=True)  # 업로드 날짜

    def __str__(self):
        return self.user_id


# Pseudonymized_data 모델
class PseudonymizedData(models.Model):
    pseudonym_id = models.CharField(max_length=50, unique=True)
    upload_data = models.ForeignKey(OriginalData, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pseudo_text = models.TextField()
    processed_data = models.DateTimeField()
    p_status = models.CharField(max_length=20)

    def __str__(self):
        return f"PseudonymizedData {self.pseudonym_id} for {self.user.username}"


# user_access_logs 모델
class UserAccessLogs(models.Model):
    log_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=50)
    access_time = models.DateTimeField(auto_now_add=True)
    log_status = models.CharField(max_length=20, choices=[('success', '성공'), ('failure', '실패')])
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"AccessLog {self.log_id} for {self.user.username}"


# Login 모델
class Login(models.Model):
    login_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    device_info = models.TextField()
    login_status = models.CharField(max_length=20, choices=[('success', '성공'), ('failure', '실패')])
    failure_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Login {self.login_id} for {self.user.username}"


# GPT 모델
class GPT(models.Model):
    history_id = models.CharField(max_length=50, unique=True)
    pseudonym_data = models.ForeignKey(PseudonymizedData, on_delete=models.CASCADE)
    upload_data = models.ForeignKey(OriginalData, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_text = models.TextField()
    response_text = models.TextField()

    def __str__(self):
        return f"GPT History {self.history_id} for {self.user.username}"
    

class FileHistory(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='file_histories'
    )
    original_content = models.TextField()
    modified_content = models.TextField()
    title = models.CharField(max_length=200)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']
        db_table = 'server_filehistory'  # 테이블 이름 명시적 지정

    def __str__(self):
        return f"{self.title} - {self.upload_date}"

class UploadedFile(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    anonymized_content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

# 프로필 생성 시그널
@receiver(post_save, sender='auth.User')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender='auth.User')
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()