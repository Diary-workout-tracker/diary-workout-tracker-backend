from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator


class CustomUniqueValidator(UniqueValidator):
	"""Кастомный валидатор уникальности email."""

	message = _("Такой email уже существует.")
