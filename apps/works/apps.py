from django.apps import AppConfig


class WorksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'works'
    verbose_name = "作品管理"
    verbose_name_plural = verbose_name
