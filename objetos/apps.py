from django.apps import AppConfig


class ObjetosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'objetos'

    def ready(self):
        import objetos.signals