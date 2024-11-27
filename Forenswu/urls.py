from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from Server import views

urlpatterns = [
    path('admin/', admin.site.urls),  # 관리자 페이지
    path('server/', include('Server.urls')),  # Server 앱 URL 포함
    path('login/', views.login_view, name='login'),  # 커스텀 로그인 뷰
    path('signup/', views.signup_view, name='signup'),
    path('main/', views.main_page, name='main'),
    path('server/logout/', auth_views.LogoutView.as_view(), name='server_logout'),  # 서버 로그아웃
    path('server/save_anonymized_data/', views.save_anonymized_data, name='save_anonymized_data'),


    # 로그인 페이지 URL은 Django 기본 LoginView를 사용
    path('server/login/', auth_views.LoginView.as_view(), name='server_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
