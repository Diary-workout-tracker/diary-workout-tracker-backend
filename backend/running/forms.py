import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Day
from .widgets import WorkoutWidget


class CastomJSONField(forms.JSONField):
	"""Кастомное поле ввода JSON."""

	def to_python(self, value: str):
		"""Валидация данных."""
		dict_value = json.loads(value.replace("'", '"'))
		workout_program = dict_value.get("workout_program")
		if not workout_program:
			error_message = "Программа тренировки обязательна."
			raise ValidationError(
				_(error_message),
				code="invalid",
				params={"value": value},
			)
		return super().to_python(value)


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
