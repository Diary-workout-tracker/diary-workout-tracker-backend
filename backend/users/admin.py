from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

admin.site.unregister(Group)

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {"fields": ("email",)}),
		("Personal info", {"fields": ("name",)}),
		("Custom Fields", {"fields": ("last_completed_training_number", "amount_of_skips")}),
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
	list_display = ("email", "name", "is_staff")
	search_fields = ("email", "name")
	ordering = ("email",)
