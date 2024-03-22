import json

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Achievement, Day, History, MotivationalPhrase, UserAchievement
from .forms import DayForm


@admin.register(MotivationalPhrase)
class MotivationalPhraseAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Мотивацонных фраз."""

	list_display = (
		"text",
		"rest",
	)
	search_fields = ("text",)
	list_filter = ("rest",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Достижений."""

	list_display = (
		"title",
		"description",
		"show_icon",
		"show_black_white_icon",
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

	@admin.display(description="Превью ЧБ иконки")
	def show_black_white_icon(self, obj: Achievement) -> str:
		"""Отображение превью ЧБ иконки достижения"""
		images_column: str = format_html("<img src='{}' style='max-height: 100px;'>", obj.black_white_icon.url)
		return images_column

	@admin.display(description="Превью иконки")
	def show_icon(self, obj: Achievement) -> str:
		"""Отображение превью иконки достижения"""
		images_column: str = format_html("<img src='{}' style='max-height: 100px;'>", obj.icon.url)
		return images_column


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Дней тренировки."""

	form = DayForm
	list_display = (
		"day_number",
		"show_workout",
	)
	list_filter = ("day_number",)

	def changeform_view(
		self, request: WSGIRequest, object_id: str | None = None, form_url: str = "", extra_context=None
	) -> HttpResponse:
		"""Формирует словарь для сериализации в JSON."""
		if request.POST:
			workout = {}
			running_pace = request.POST.get("running_pace")
			total_duration = 0
			if running_pace:
				workout["running_pace"] = running_pace
			i = 1
			workout["workout_program"] = []
			while True:
				pace = request.POST.get(f"pace-{i}")
				duration = request.POST.get(f"duration-{i}")
				if not pace or not duration:
					break
				workout["workout_program"].append({"pace": pace, "duration": duration})
				total_duration += int(duration)
				i += 1
			workout["total_duration"] = total_duration
			copy_values = request.POST.copy()
			copy_values["workout"] = json.dumps(workout)
			request.POST = copy_values
		return super().changeform_view(request, object_id, form_url, extra_context)

	@admin.display(description="Тренировка")
	def show_workout(self, obj: Day) -> str:
		"""Отображения поля для админки."""
		stage_column: list = []
		data = obj.workout
		if data:
			for workout in data["workout_program"]:
				stage_column.append(f"{workout['pace']} - {workout['duration']} c.")
			running_pace = data.get("running_pace")
			if running_pace:
				stage_column.append(running_pace)
			return ", ".join(stage_column)
		return format_html(f"<span style='color: red;'>{_('Тренировка введена некорректно')}</span>")


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
		"user_id",
	)
	search_fields = (
		"motivation_phrase",
		"user_id",
	)

	@admin.display(description="Превью изображения маршрута")
	def show_image(self, obj: History) -> str | None:
		"""Отображение превью изображения маршрута."""
		if obj.image:
			return format_html("<img src='{}'' style='max-height: 100px;'>", obj.image.url)
		return


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
