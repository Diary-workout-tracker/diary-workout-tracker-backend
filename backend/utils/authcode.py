from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
from .mailsender import MailSender
from django.conf import settings
import random

User = get_user_model()


class AuthCode:
	"""Класс обслуживает одноразовый код для восстановления доступа.
	Умеет генерировать код, отправлять его на е-мейл, проверять валидность,
	 у класса настраивается отправщик емейлов."""

	def __init__(self, user) -> None:
		if not isinstance(user, User):
			raise ValidationError(f"{user} is not a User instance")
		self._sender = None
		self._user = user

	def create_code(self) -> None:
		self._store_code(self._generate_code())
		self._send_code()

	def code_is_valid(self, code: int) -> bool:
		return code == self.code

	def _generate_code(self) -> str:
		return str(random.randint(0, 9999)).zfill(4)

	def _store_code(self, code: str) -> None:
		cache.set(self._user.email, code, settings.ACCESS_RESTORE_CODE_TTL_SECONDS)

	def _send_code(self) -> None:
		if not self._sender:
			raise ValidationError("Cannot send code: sender not set.")
		self._sender.send_mail(self._user.email, self.code)

	def set_sender(self, sender: MailSender) -> None:
		self._sender = sender

	@property
	def code(self):
		return cache.get(self._user.email)
