from django.contrib import admin
from django.utils.html import format_html

from .models import Achievement, Day, History, Stage


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
		"show_workout",
		"workout_info",
	)
	filter_horizontal = ("workout",)
	search_fields = (
		"motivation_phrase",
		"workout_info",
	)
	list_filter = ("day_number",)

	@admin.display(description="Тренеровка")
	def show_workout(self, obj: Day) -> str:
		stage_column: list = []
		for workout in obj.workout.all():
			minutes = round(workout.duration.total_seconds() // 60)
			text = dict(Stage.TYPE)[workout.pace]
			stage_column.append(f"{str(minutes)}-{text}")
		return ", ".join(stage_column)


@admin.register(History)
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
	search_fields = ("training_day",)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
	list_display = ("duration", "pace")
	list_filter = ("pace",)
	search_fields = ("duration", "pace")
