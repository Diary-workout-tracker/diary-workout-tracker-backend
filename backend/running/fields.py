import json
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CastomJSONField(forms.JSONField):
	"""Кастомное поле ввода JSON."""

	def to_python(self, value: str) -> Any:
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
