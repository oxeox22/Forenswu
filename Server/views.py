from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import FileHistory, UploadedFile
import json
import openai
from django.conf import settings  # OpenAI API 키를 settings에서 불러오기
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from django.contrib.auth import get_user_model  # 상단에 추가
from openai import OpenAI  # 상단에 import 문 수정
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import pytesseract
from pdf2image import convert_from_path
import tempfile
import os
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests
import uuid
import time

# OpenAI API 키 설정
openai.api_key = settings.OPENAI_API_KEY

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# views.py 상단에 추가
if os.name == 'nt':  # Windows인 경우
    POPPLER_PATH = r"D:\Release-24.08.0-0\poppler-24.08.0\Library\bin"  # poppler의 bin 폴더 경로로 수정
else:
    POPPLER_PATH = None

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # 사용자가 등록된 후 로그인 처리
            user = form.save()  # 회원가입 처리
            login(request, user)  # 바로 로그인
            return redirect('main')  # 회원가입 후 메인 페이지로 리디렉션
        else:
            # 폼이 유효하지 않으면, 오류 메시지와 함께 폼을 다시 렌더링
            print(form.errors)  # 오류 메시지 출력 (디버깅용)
    else:
        form = UserCreationForm()

    return render(request, 'Server/signup.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # 사용자가 정상적으로 가입되면
            form.save()  # 회원가입 처리
            return redirect('login')  # 회원가입 후 로그인 페이지로 리디렉션
        else:
            # 폼이 유효하지 않으면, 오류 메시지와 함께 폼을 다시 렌더링
            print(form.errors)  # 오류 메시지 출력 (디버깅용)
    else:
        form = UserCreationForm()

    return render(request, 'Server/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # 로그인 처리
                return redirect('main')  # 로그인 후 메인 페이지로 리디렉션
            else:
                form.add_error(None, '아이디 또는 비밀번호가 잘못되었습니다.')
    else:
        form = AuthenticationForm()

    return render(request, 'Server/login.html', {'form': form})

def logout_view(request):
    logout(request)  # 로그아웃 처리
    return redirect('Server/login.html')  # 로그아웃 후 로그인 페이지로 리디렉션

def main_page(request):
    return render(request, 'Server/main.html')


@csrf_exempt
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        try:
            uploaded_file = request.FILES["file"]
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            if file_extension in ['.pdf', '.jpg', '.jpeg', '.png']:
                # 이미지 또는 PDF 파일 처리
                api_url = settings.CLOVA_OCR_API_URL
                secret_key = settings.CLOVA_OCR_SECRET_KEY

                # PDF인 경우 이미지로 변환
                if file_extension == '.pdf':
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                        for chunk in uploaded_file.chunks():
                            temp_pdf.write(chunk)
                        temp_pdf_path = temp_pdf.name

                    # poppler 경로 지정하여 PDF 변환
                    if os.name == 'nt':  # Windows인 경우
                        images = convert_from_path(temp_pdf_path, poppler_path=POPPLER_PATH)
                    else:
                        images = convert_from_path(temp_pdf_path)
                    extracted_text = ""

                    # 각 페이지를 개별적으로 OCR 처리
                    for i, image in enumerate(images):
                        # 이미지를 임시 파일로 저장
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_img:
                            image.save(temp_img, 'JPEG')
                            temp_img_path = temp_img.name

                        # Clova OCR API 요청
                        request_json = {
                            'images': [
                                {
                                    'format': 'jpg',
                                    'name': f'page_{i+1}'
                                }
                            ],
                            'requestId': str(uuid.uuid4()),
                            'version': 'V2',
                            'timestamp': int(round(time.time() * 1000))
                        }

                        payload = {'message': json.dumps(request_json).encode('UTF-8')}
                        
                        with open(temp_img_path, 'rb') as image_file:
                            files = [('file', image_file)]
                            headers = {'X-OCR-SECRET': secret_key}
                            
                            response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
                            
                            if response.status_code == 200:
                                # OCR 결과 텍스트 추출
                                for field in response.json()['images'][0]['fields']:
                                    extracted_text += field['inferText'] + " "
                                extracted_text += "\n\n"  # 페이지 구분을 위한 줄바꿈

                        # 임시 이미지 파일 삭제
                        os.unlink(temp_img_path)

                    # 임시 PDF 파일 삭제
                    os.unlink(temp_pdf_path)

                else:  # 이미지 파일인 경우
                    # 이미지를 임시 파일로 저장
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_img:
                        for chunk in uploaded_file.chunks():
                            temp_img.write(chunk)
                        temp_img_path = temp_img.name

                    request_json = {
                        'images': [
                            {
                                'format': file_extension[1:],  # 점(.) 제거
                                'name': 'image'
                            }
                        ],
                        'requestId': str(uuid.uuid4()),
                        'version': 'V2',
                        'timestamp': int(round(time.time() * 1000))
                    }

                    payload = {'message': json.dumps(request_json).encode('UTF-8')}
                    
                    with open(temp_img_path, 'rb') as image_file:
                        files = [('file', image_file)]
                        headers = {'X-OCR-SECRET': secret_key}
                        
                        response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
                        
                        extracted_text = ""
                        if response.status_code == 200:
                            for field in response.json()['images'][0]['fields']:
                                extracted_text += field['inferText'] + " "

                    # 임시 이미지 파일 삭제
                    os.unlink(temp_img_path)

                # UploadedFile 모델에 저장
                if request.user.is_authenticated:
                    new_file = UploadedFile.objects.create(
                        user=request.user,
                        title=uploaded_file.name,
                        content=extracted_text
                    )
                else:
                    return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

                return JsonResponse({
                    "message": "파일이 성공적으로 처리되었습니다.",
                    "file_id": new_file.id,
                    "extracted_text": extracted_text
                })

            elif file_extension == '.txt':
                # 기존 텍스트 파일 처리 로직
                file_content = uploaded_file.read().decode("utf-8")
                
                if request.user.is_authenticated:
                    new_file = UploadedFile.objects.create(
                        user=request.user,
                        title=uploaded_file.name,
                        content=file_content
                    )
                else:
                    return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

                return JsonResponse({
                    "message": "파일이 성공적으로 업로드되었습니다.",
                    "file_id": new_file.id,
                    "extracted_text": file_content
                })

            else:
                return JsonResponse({"error": "지원하지 않는 파일 형식입니다. PDF, 이미지 또는 TXT 파일만 업로드 가능합니다."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"파일 업로드 중 오류 발생: {str(e)}"}, status=500)

    return render(request, "server/upload.html")


def pseudonymize(request):
    if request.method == 'GET':
        file_content = request.GET.get('fileContent', '')
        return render(request, 'Server/pseudonymize.html', {'file_content': file_content})
    return render(request, 'Server/pseudonymize.html')


def gpt_page(request):
    try:
        files = []  # 기본값으로 빈 리스트 설정
        selected_file = None

        # 로그인한 사용자인 경우에만 파일 목록 가져오기
        if request.user.is_authenticated:
            files = UploadedFile.objects.filter(
                user=request.user,
                anonymized_content__isnull=False
            )
            
            if "file_id" in request.GET:
                file_id = request.GET.get("file_id")
                selected_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)

        return render(request, "server/gpt.html", {
            "files": files, 
            "selected_file": selected_file,
            "is_authenticated": request.user.is_authenticated
        })

    except Exception as e:
        print(f"Error in gpt_page: {e}")
        return render(request, "server/gpt.html", {
            "files": [], 
            "error": "파일 목록을 불러올 수 없습니다.",
            "is_authenticated": request.user.is_authenticated
        })


@login_required
def get_uploaded_files(request):
    try:
        files_list = []
        if request.user.is_authenticated:
            # 로그인한 사용자의 파일만 필터링
            files = UploadedFile.objects.filter(
                user=request.user,
                anonymized_content__isnull=False
            ).values('id', 'title', 'anonymized_content', 'created_at').order_by('-created_at')
            
            files_list = [
                {
                    "id": file["id"],
                    "title": file["title"],
                    "anonymized_content": file["anonymized_content"],
                    "uploaded_at": file["created_at"].strftime("%Y-%m-%d")
                }
                for file in files
            ]
        return JsonResponse(files_list, safe=False)
    except Exception as e:
        print(f"Error in get_uploaded_files: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def save_anonymized_data(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id', None)
        original_text = request.POST.get('original_text', '')
        anonymized_text = request.POST.get('anonymized_text', '')

        if not user_id:
            user_id = "anonymous"

        print("Received data:", user_id, original_text, anonymized_text)

        UploadedFile.objects.create(
            user_id=user_id,
            original_text=original_text,
            processed_data=anonymized_text,
            p_status='processed'
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def list_data(request):
    data = UploadedFile.objects.values('user_id', 'original_text', 'processed_data', 'p_status')
    return JsonResponse(list(data), safe=False)

def howtouse_page(request):
    return render(request, 'Server/howtouse.html')

@login_required(login_url='/server/login/')
def original_page(request):
    try:
        histories = FileHistory.objects.filter(user=request.user).order_by('-upload_date')
        return render(request, 'Server/original.html', {'histories': histories})
    except Exception as e:
        print(f"Error in original_page view: {e}")
        histories = []
        return render(request, 'Server/original.html', {'histories': histories})

# 검색 페이지 뷰
def search_page(request):
    return render(request, 'Server/search.html')

# 증명서 페이지 뷰
def certificate_page(request):
    return render(request, 'Server/certificate.html')


@csrf_exempt
def ask_gpt(request):
    if request.method == "POST":
        try:
            # JSON 데이터 파싱
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "잘못된 JSON 데이터입니다."}, status=400)

            question = data.get("question", "")
            file_id = data.get("file_id", "")

            if not question or not file_id:
                return JsonResponse({"error": "질문 또는 파일 ID가 비어 있습니다."}, status=400)

            # 파일 데이터 조회
            selected_file = get_object_or_404(UploadedFile, id=file_id)
            file_content = selected_file.anonymized_content  # 가명화된 내용 사용

            # OpenAI API 호출 (새로운 형식)
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"다음 텍스트를 참고하여 질문에 답변해주세요:\n\n{file_content}\n\n질: {question}"}
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content
                return JsonResponse({"answer": answer}, json_dumps_params={'ensure_ascii': False})

            except Exception as e:
                print(f"OpenAI API 오류: {str(e)}")
                return JsonResponse({"error": f"OpenAI API 오류: {str(e)}"}, status=500)

        except Exception as e:
            print(f"서버 오류: {str(e)}")
            return JsonResponse({"error": f"서버 오류: {str(e)}"}, status=500)

    return JsonResponse({"error": "GET 요청은 허용되지 않습니다."}, status=405)

@login_required
def profile(request):
    if request.method == 'POST':
        # POST 요청: 사용자가 이미지를 업로드하거나 변경한 경우
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()  # 변경된 프로필 저장
            return redirect('profile')  # 저장 후 다시 프로필 페이지로 이동
    else:
        # GET 요청: 기존 프로필 정보를 가져옴
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'Server/profile.html', {'form': form})  # 폼을 템플릿에 전달

@login_required
def profile_view(request):
    # 프로필 보기
    return render(request, 'Server/profile.html')

@login_required
def profile_update(request):
    # 프로필 수정
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('/server/original/')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'Server/profile_update.html', {'form': form})

@csrf_exempt
@login_required
def save_modified_file(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # FileHistory에 저장
            FileHistory.objects.create(
                user=request.user,
                original_content=data.get('original_content'),
                modified_content=data.get('modified_content'),
                title=data.get('title', '무제')
            )
            
            # UploadedFile에도 저장 (GPT용)
            UploadedFile.objects.create(
                user=request.user,  # 사용자 정보 추가
                title=data.get('title', '무제'),
                content=data.get('original_content'),
                anonymized_content=data.get('modified_content')
            )
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def view_file_detail(request, history_id):
    history = get_object_or_404(FileHistory, id=history_id, user=request.user)
    return render(request, 'Server/file_detail.html', {'history': history})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            return redirect('original_page')
        else:
            messages.error(request, '비밀번호 변경에 실패했습니다. 입력한 정보를 확인해주세요.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'Server/pwd.html', {'form': form})