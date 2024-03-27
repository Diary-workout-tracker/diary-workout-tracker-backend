import re
import json

from django.contrib import admin, messages
from django.contrib.messages.storage import default_storage
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import DayForm, HistoryForm
from .models import Achievement, Day, History, MotivationalPhrase, UserAchievement


DEBUG = settings.DEBUG


@admin.register(MotivationalPhrase)
class MotivationalPhraseAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Мотивацонных фраз."""

	list_display = (
		"text",
		"rest",
	)
	search_fields = ("text",)
	list_filter = ("rest",)
	if not DEBUG:
		readonly_fields = ("rest",)

	def has_add_permission(self, request: WSGIRequest) -> bool:
		"""Разрешение на добавление объекта."""
		return DEBUG

	def has_delete_permission(self, request: WSGIRequest, obj: MotivationalPhrase | None = None) -> bool:
		"""Разрешение на удаление объекта."""
		return DEBUG


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
	"""Отображение в админ панели Достижений."""

	list_display = (
		"id",
		"title",
		"description",
		"show_icon",
		"show_black_white_icon",
		"reward_points",
	)
	search_fields = (
		"title",
		"description",
	)
	list_filter = ("reward_points",)
	if not DEBUG:
		readonly_fields = ("id",)

	def has_add_permission(self, request: WSGIRequest) -> bool:
		"""Разрешение на добавление объекта."""
		return DEBUG

	def has_delete_permission(self, request: WSGIRequest, obj: Achievement | None = None) -> bool:
		"""Разрешение на удаление объекта."""
		return DEBUG

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
	if not DEBUG:
		readonly_fields = ("day_number",)

	def has_add_permission(self, request: WSGIRequest) -> bool:
		"""Разрешение на добавление объекта."""
		return DEBUG

	def has_delete_permission(self, request: WSGIRequest, obj: Day | None = None) -> bool:
		"""Разрешение на удаление объекта."""
		return DEBUG

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
			workout["workout_program"] = []
			post_keys = request.POST.keys()
			r = re.compile("pace-*")
			count_fields_workout_program = len(list(filter(r.match, post_keys)))
			for i in range(1, count_fields_workout_program + 1):
				pace = request.POST.get(f"pace-{i}")
				duration = request.POST.get(f"duration-{i}")
				if not pace or not duration:
					continue
				workout["workout_program"].append({"pace": pace, "duration": duration})
				total_duration += int(duration)
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

	form = HistoryForm
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
	if not DEBUG:
		actions = None
	error_delete = False
	update_readonly_fields = ("training_day", "user_id")

	def get_readonly_fields(self, request: WSGIRequest, obj: History | None = None) -> list:
		"""Запрещает редактировать поле с днём тренировки и пользователем."""
		if obj and not DEBUG:
			return self.update_readonly_fields
		return self.readonly_fields

	def save_model(self, request: WSGIRequest, obj: History, form: HistoryForm, change: bool) -> None:
		"""Сохраняет объект и обновляет последнюю тренировку пользователя."""
		if obj.pk is None and not DEBUG:
			obj.save()
			user = obj.user_id
			user.last_completed_training = obj
			user.save()
			return
		obj.save()

	def delete_model(self, request: WSGIRequest, obj: History) -> None:
		"""Удаляет объект и обновляет последнюю тренировку пользователя."""
		if not DEBUG:
			user = obj.user_id
			if user.last_completed_training != obj:
				self.error_delete = True
				return
			day_number = obj.training_day.day_number
			if day_number > 1:
				user.last_completed_training = History.objects.get(
					user_id=user, training_day=Day.objects.get(day_number=day_number - 1)
				)
				user.save()
		obj.delete()

	def response_delete(self, request: WSGIRequest, obj_display: str, obj_id: int) -> HttpResponseRedirect:
		"""Меняет сообщение об удалении в случае ошибки."""
		response = super().response_delete(request, obj_display, obj_id)
		if self.error_delete:
			self.error_delete = False
			request._messages = default_storage(request)
			self.message_user(
				request,
				_("%(name)s “%(obj)s” не является последней тренировкой пользователя.")
				% {
					"name": self.opts.verbose_name,
					"obj": obj_display,
				},
				messages.ERROR,
			)
		return response

	@admin.display(description="Превью изображения маршрута")
	def show_image(self, obj: History) -> str | None:
		"""Отображение превью изображения маршрута."""
		if obj.image:
			return format_html("<img src='{}'' style='max-height: 100px;'>", obj.image.url)


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

	def has_delete_permission(self, request: WSGIRequest, obj: UserAchievement | None = None) -> bool:
		"""Разрешение на удаление объекта."""
		return DEBUG

	def has_change_permission(self, request: WSGIRequest, obj: UserAchievement | None = None) -> bool:
		"""Разрешение на изменение объекта."""
		return DEBUG
