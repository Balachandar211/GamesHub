from django.apps import AppConfig


class GamesbuzzConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'GamesBuzz'

    def ready(self):
        import GamesBuzz.signals
