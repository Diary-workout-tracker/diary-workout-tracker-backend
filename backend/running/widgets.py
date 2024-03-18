import json

from django import forms


class WorkoutWidget(forms.Widget):
	"""Кастомный widget этапа тренировки."""

	template_name = "forms/widgets/workout_widget.html"

	class Media:
		js = ("core/js/workout_program.js",)
		css = {
			"all": ["core/css/workout_program.css"],
		}

	def format_value(self, value: str) -> dict:
		"""Преоразует строку в словарь."""
		return json.loads(value.replace("'", '"'))
