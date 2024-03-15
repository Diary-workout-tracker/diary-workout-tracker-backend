from django.contrib import admin
from django.utils.html import format_html

from .models import Achievement, Day, History, MotivationalPhrase, UserAchievement


@admin.register(MotivationalPhrase)
class MotivationalPhraseAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Мотивацонных фраз."""

	list_display = ("text", "rest")
	search_fields = ("text",)
	list_filter = ("rest",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Достижений."""

	list_display = (
		"title",
		"description",
		"show_icon",
		"stars",
		"reward_points",
	)
	search_fields = (
		"title",
		"description",
	)
	list_filter = (
		"stars",
		"reward_points",
	)

	@admin.display(description="Превью иконки")
	def show_icon(self, obj: Achievement) -> str:
		"""Отображение превью иконки достижения"""
		images_column: str = format_html('<img src="{}" style="max-height: 100px;">', obj.icon.url)
		return images_column


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Дней тренировки."""

	list_display = (
		"day_number",
		"show_workout",
	)
	list_filter = ("day_number",)

	@admin.display(description="Тренировка")
	def show_workout(self, obj: Day) -> str:
		"""
		Отображения поля для админки
		Пример заполнения:
		{
		  "workout":
		        [
		          {"duration": 15, "pace": "бег"},
		          {"duration": 10, "pace": "ходьба"}
		        ]
		}
		"""
		stage_column: list = []
		data = obj.workout["workout"]
		for workout in data:
			stage_column.append(f"{workout['duration']}-{workout['pace']}")
		return ", ".join(stage_column)


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
	"""Отображение в админ панели истории тренировки."""

	list_display = (
		"training_start",
		"training_end",
		"completed",
		"show_image",
		"motivation_phrase",
		"cities",
		"training_day",
		"distance",
		"max_speed",
		"avg_speed",
		"user_id",
	)
	list_filter = (
		"completed",
		"training_end",
		"cities",
		"user_id",
	)
	search_fields = (
		"training_end",
		"motivation_phrase",
		"cities",
		"user_id",
	)

	@admin.display(description="Превью изображения маршрута")
	def show_image(self, obj: History) -> str:
		"""Отображение превью изображения маршрута."""
		return format_html('<img src="{}" style="max-height: 100px;">', obj.image.url)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Тренировок."""

	list_display = (
		"user_id",
		"achievement_id",
		"achievement_date",
	)
	search_fields = (
		"user_id__username",
		"achievement_id__title",
		"achievement_id__description",
	)
