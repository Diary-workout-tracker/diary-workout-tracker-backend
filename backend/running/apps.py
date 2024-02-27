from django.apps import AppConfig


class RuningConfig(AppConfig):
	default_auto_field = "django.db.models.BigAutoField"
	name = "running"
	verbose_name = "Бег"
