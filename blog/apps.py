from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    # Starts signals to create author profile.
    def ready(self):
        from . import signals
