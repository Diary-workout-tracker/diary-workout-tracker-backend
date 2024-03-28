from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Day, History
from .widgets import WorkoutWidget
from .fields import CastomJSONField


DEBUG = settings.DEBUG


class DayForm(forms.ModelForm):
	"""Кастомная форма дня тренировки."""

	workout = CastomJSONField(label=Day._meta.get_field("workout").verbose_name, widget=WorkoutWidget)

	class Meta:
		fields = (
			"day_number",
			"workout",
			"workout_info",
		)
		model = Day


class HistoryForm(forms.ModelForm):
	"""Кастомная форма админки History."""

	class Meta:
		fields = "__all__"
		model = History

	def _validate_date(self, cleaned_data: dict) -> None:
		"""Валидация дат."""
		training_start = cleaned_data.get("training_start")
		training_end = cleaned_data.get("training_end")
		if None not in (training_start, training_end) and training_start >= training_end:
			self.add_error("training_start", ValidationError(_("Начало тренировки должно быть раньше конца.")))
			self.add_error("training_end", ValidationError(_("Конец тренировки должен быть позже начала.")))

	def _validate_history(self, cleaned_data: dict) -> None:
		"""Валидация дня тренировки."""
		new_object = self.instance.pk is None
		user_id = cleaned_data.get("user_id")
		training_day = cleaned_data.get("training_day")
		if None not in (new_object, user_id, training_day):
			last_completed_training = user_id.last_completed_training
			new_history_day_number = training_day.day_number
			if last_completed_training:
				last_day_number = last_completed_training.training_day.day_number
				if last_day_number + 1 != new_history_day_number:
					self.add_error(
						"training_day", ValidationError(_(f"День тренировки должен быть равен {last_day_number + 1}."))
					)
				return
			if new_history_day_number != 1:
				self.add_error("training_day", ValidationError(_("День тренировки должен быть равен 1.")))

	def clean(self) -> dict:
		"""Валидация формы."""
		cleaned_data = super().clean()
		if not DEBUG:
			self._validate_date(cleaned_data)
			self._validate_history(cleaned_data)
		return cleaned_data
