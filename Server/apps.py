from django.apps import AppConfig
class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Server'

    def ready(self):
        pass  # 또는 빈 메서드 그대로 두기
