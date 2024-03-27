from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext_lazy as _
from .models import User as ClassUser


admin.site.unregister(Group)

User = get_user_model()
DEBUG = settings.DEBUG


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
	"""Админка для юзера."""

	fieldsets = (
		(None, {"fields": ("email",)}),
		(_("Личная информация"), {"fields": ("name",)}),
		(_("Кастомные поля"), {"fields": ("last_completed_training", "date_last_skips", "amount_of_skips", "avatar")}),
	)
	add_fieldsets = (
		(
			None,
			{
				"classes": ("wide",),
				"fields": ("email", "password1", "password2"),
			},
		),
	)
	list_display = (
		"avatar_display",
		"email",
		"name",
		"is_staff",
	)
	search_fields = ("email", "name")
	if not DEBUG:
		readonly_fields = (
			"last_completed_training",
			"date_last_skips",
			"email",
		)
	ordering = ("email",)

	def has_add_permission(self, request: WSGIRequest) -> bool:
		"""Разрешение на добавление объекта."""
		return DEBUG

	def has_delete_permission(self, request: WSGIRequest, obj: ClassUser | None = None) -> bool:
		"""Разрешение на удаление объекта."""
		return DEBUG
