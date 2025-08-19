from django.apps import AppConfig


class AgreementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agreement'
    verbose_name = "协议条款管理"
    verbose_name_plural = verbose_name
