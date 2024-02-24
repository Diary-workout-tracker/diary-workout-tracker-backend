from django.contrib import admin
from django.utils.html import format_html

from .models import Achievement, Day, Training


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Достижений."""

	list_display = (
		"name",
		"description",
		"show_icon",
		"stars",
		"reward_points",
	)
	search_fields = (
		"name",
		"description",
	)
	list_filter = (
		"stars",
		"reward_points",
	)

	@admin.display(description="Превью иконки")
	def show_icon(self, obj: Achievement) -> str:
		images_column: str = format_html('<img src="{}" style="max-height: 100px;">', obj.image.url)
		return images_column


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Дней тренеровки."""

	list_display = (
		"day_number",
		"motivation_phrase",
		"training_info",
		"training_time",
		"pace",
	)
	search_fields = (
		"motivation_phrase",
		"training_info",
		"pace",
	)
	list_filter = (
		"training_time",
		"pace",
	)


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Тренеровок."""

	list_display = (
		"training_date",
		"completed",
		"training_day",
		"distance",
		"max_speed",
		"avg_speed",
	)
	list_filter = (
		"completed",
		"training_day",
	)
	search_fields = ("training_day__day_number",)
