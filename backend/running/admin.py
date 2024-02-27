from django.contrib import admin
from django.contrib.admin import ModelAdmin, register
from django.utils.html import format_html


from .models import Achievement, Day, History, MotivationalPhrase, RecreationPhrase, UserAchievement


@register(MotivationalPhrase)
class MotivationalPhraseAdmin(ModelAdmin):
	list_display = ("text",)


@register(RecreationPhrase)
class RecreationPhraseAdmin(ModelAdmin):
	list_display = ("text",)


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
	"""Отображение в админ панели Дней тренеровки."""

	list_display = (
		"day_number",
		"motivation_phrase",
		"show_workout",
	)
	search_fields = ("motivation_phrase",)
	list_filter = ("day_number",)

	@admin.display(description="Тренеровка")
	def show_workout(self, obj: Day) -> str:
		"""
		Отображения поля для админки
		Пример заполнения:
		{
		  "workout":
		        [
		          {"duration": 15, "pace": "бег"},
		          {"duration": 10, "pace": "ходьба]"}
		        ]
		}
		"""
		stage_column: list = []
		data = obj.workout["workout"]
		for workout in data:
			stage_column.append(f"{str(workout['duration'])}-{workout['pace']}")
		return ", ".join(stage_column)


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
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


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Тренеровок."""

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
