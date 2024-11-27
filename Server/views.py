from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedFile
import json
import openai
from django.conf import settings  # OpenAI API 키를 settings에서 불러오기
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm

# OpenAI API 키 설정
openai.api_key = settings.OPENAI_API_KEY


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
            file_content = uploaded_file.read().decode("utf-8")  # 파일 내용을 텍스트로 저장

            # UploadedFile 모델에 데이터 저장
            new_file = UploadedFile.objects.create(
                title=uploaded_file.name,
                content=file_content  # 텍스트 내용
            )
            return JsonResponse({"message": "File uploaded successfully", "file_id": new_file.id})
        except UnicodeDecodeError:
            return JsonResponse({"error": "Invalid file format. Only text files are supported."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return render(request, "server/upload.html")


def pseudonymize(request):
    file_id = request.GET.get('file_id')

    if file_id:
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        file_content = uploaded_file.content
        anonymized_content = file_content.replace("홍길동", "****")  # 간단한 가명화 예제

        uploaded_file.anonymized_content = anonymized_content
        uploaded_file.save()
    else:
        file_content = "파일 내용이 없습니다."
        anonymized_content = "가명화된 내용이 없습니다."

    return render(request, "server/pseudonymize.html", {
        "file_content": file_content,
        "anonymized_content": anonymized_content,
        "file_id": file_id if file_id else None
    })


def gpt_page(request):
    try:
        files = UploadedFile.objects.filter(anonymized_content__isnull=False)
        selected_file = None

        if "file_id" in request.GET:
            file_id = request.GET.get("file_id")
            selected_file = get_object_or_404(UploadedFile, id=file_id)

        return render(request, "server/gpt.html", {"files": files, "selected_file": selected_file})

    except Exception as e:
        print(f"Error in gpt_page: {e}")
        return render(request, "server/gpt.html", {"files": [], "error": "파일 목록을 불러올 수 없습니다."})


def get_uploaded_files(request):
    try:
        files = UploadedFile.objects.values("id", "title", "created_at").order_by("-created_at")
        files_list = [
            {
                "id": file["id"],
                "title": file["title"],
                "uploaded_at": file["created_at"].strftime("%Y-%m-%d"),
            }
            for file in files
        ]
        return JsonResponse(files_list, safe=False)
    except Exception as e:
        print(f"Error in get_uploaded_files: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
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

def original_page(request):
    return render(request, 'Server/original.html')


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
            file_content = selected_file.anonymized_content

            # OpenAI API 호출
            openai.api_key = settings.OPENAI_API_KEY

            chat_history = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"File content: {file_content}"},
            ]
            chat_history.append({"role": "user", "content": question})

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=chat_history,
                    max_tokens=200,
                    temperature=0.7,
                )
                answer = response["choices"][0]["message"]["content"]
                return JsonResponse({"answer": answer}, json_dumps_params={'ensure_ascii': False})

            except openai.error.OpenAIError as e:
                return JsonResponse({"error": f"OpenAI API 오류: {str(e)}"}, status=500)

        except Exception as e:
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