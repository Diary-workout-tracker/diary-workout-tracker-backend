from django.conf import settings
from django.utils import timezone
from rest_framework import throttling


class CodeRequestThrottle(throttling.BaseThrottle):
	"""Класс для тротлинга запросов кода.
	Настраиваемое решение со следующей логикой: если код запрашивается
	больше num_requests раз в течение duration минут, включается запрет
	на дельнейшие запросы, который длится cooldown минут."""

	_history = {}

	def __init__(self) -> None:
		self._duration = settings.ACCESS_RESTORE_CODE_THROTTLING["duration"]
		self._num_requests = settings.ACCESS_RESTORE_CODE_THROTTLING["num_requests"]
		self._cooldown = settings.ACCESS_RESTORE_CODE_THROTTLING["cooldown"]
		self._user_email = None
		self._now = None

	def allow_request(self, request, view):
		self._now = timezone.now()
		self._user_email = request.data.get("email")
		self._update_history()
		return self._validate_request()

	def _validate_request(self):
		if len(self._history[self._user_email]) <= self._num_requests:
			return True
		self._history[self._user_email].pop(0)
		return self._now - self._history[self._user_email][-2] >= self._cooldown

	def _update_history(self):
		if self._user_email not in self._history:
			self._history[self._user_email] = []
		self._history[self._user_email].append(self._now)

	def wait(self):
		last_request_time = self._history[self._user_email][-2]
		next_allowed_time = last_request_time + self._cooldown
		return (next_allowed_time - self._now).total_seconds()
