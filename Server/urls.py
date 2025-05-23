from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('pseudonymize/', views.pseudonymize, name='pseudonymize'),
    path('save_anonymized_data/', views.save_anonymized_data, name='save_anonymized_data'),
    path('list_data/', views.list_data, name='list_data'),
    path('gpt/', views.gpt_page, name='gpt_page'),
    path('ask_gpt/', views.ask_gpt, name='ask_gpt'),
    path('get_uploaded_files/', views.get_uploaded_files, name='get_uploaded_files'),
    path('original/', views.original_page, name='original_page'),
    path('howtouse/', views.howtouse_page, name='howtouse_page'),
    path('main/', views.main_page, name='main_page'),  # 메인 페이지 URL
    path('search/', views.search_page, name='search_page'),  # 검색 페이지 추가
    path('certificate/', views.certificate_page, name='certificate_page'),  # 증명서 페이지 추가
    path('mypage/', views.original_page, name='mypage_page'),  # 마이페이지를 기존 original과 동일하게 처리
    path('login/', views.login_view, name='login'),  # 로그인 페이지
    path('signup/', views.signup_view, name='signup'),  # 회원가입 페이지
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('save_modified_file/', views.save_modified_file, name='save_modified_file'),
    path('file_detail/<int:history_id>/', views.view_file_detail, name='view_file_detail'),
    path('pwd/', views.change_password, name='change_password'),
    path('upload_file/', views.upload_file, name='upload_file'),
]