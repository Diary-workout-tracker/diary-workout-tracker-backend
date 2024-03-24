from django.conf import settings
from django.utils import timezone
from rest_framework import throttling


class DurationCooldownRequestThrottle(throttling.BaseThrottle):
	"""Класс для тротлинга запросов и вводов кода.
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
		self._now = timezone.localtime()
		self._user_email = request.data.get("email")
		self._refresh_history()
		if len(self._history[self._user_email]) < self._num_requests:
			self._history[self._user_email].append(self._now)
			return True
		if self.wait() > 0:
			return False
		self._history[self._user_email] = [self._now]
		return True

	def wait(self):
		return (self._cooldown - (self._now - self._history[self._user_email][-1])).total_seconds()

	def _refresh_history(self):
		if self._user_email not in self._history:
			self._history[self._user_email] = []
		self._history[self._user_email] = [
			t for t in self._history[self._user_email] if t >= self._now - self._duration
		]
