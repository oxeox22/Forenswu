from django.db import models

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

class UploadedFile(models.Model):
    title = models.CharField(max_length=255)  # 파일 제목
    content = models.TextField()  # 파일 내용
    anonymized_content = models.TextField(null=True, blank=True)  # 가명화된 텍스트
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title