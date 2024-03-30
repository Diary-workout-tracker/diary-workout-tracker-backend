import base64
import datetime
import re

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
	"""Класс для сериализации изображения и десериализации URI."""

	def to_internal_value(self, data):
		"""Декодирование base64 в файл."""
		if isinstance(data, str) and data.startswith("data:image"):
			format, imgstr = data.split(";base64,")
			ext = format.split("/")[-1]
			data = ContentFile(
				base64.b64decode(imgstr),
				name=str(datetime.datetime.now().timestamp()) + "." + ext,
			)
		return super().to_internal_value(data)

	def to_representation(self, value):
		"""Возвращает полный url изображения."""
		if value:
			uri = self.context["request"].build_absolute_uri(
				f"{settings.MEDIA_URL}{value}" if isinstance(value, str) else value.url
			)
			if set(settings.CSRF_TRUSTED_ORIGINS).issubset(("http://127.0.0.1", "http://localhost")):
				return uri
			return re.sub("http", "https", uri, 1)
