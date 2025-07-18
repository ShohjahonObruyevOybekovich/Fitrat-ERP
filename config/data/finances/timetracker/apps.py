from django.apps import AppConfig


class TimetrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.finances.timetracker'

    def ready(self):
        import data.finances.timetracker.signals