from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

admin.site.unregister(Group)

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
	"""Админка для юзера."""

	fieldsets = (
		(None, {"fields": ("email",)}),
		(_("Личная информация"), {"fields": ("name",)}),
		(
			_("Кастомные поля"),
			{"fields": ("last_completed_training", "date_last_skips", "amount_of_skips", "avatar", "total_m_run")},
		),
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
	list_display = ("avatar_display", "email", "name", "is_staff")
	search_fields = ("email", "name")
	ordering = ("email",)
