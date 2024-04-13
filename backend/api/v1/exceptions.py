from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback


class CustomThrottled:
	def __init__(self, exc) -> None:
		self._exc = exc

	def build_response(self):
		data = {
			"detail": [f"{self._exc.wait}"],
		}
		return Response(data, status=self._exc.status_code, headers=self._build_headers)

	@property
	def _build_headers(self):
		headers = {}
		if getattr(self._exc, "auth_header", None):
			headers["WWW-Authenticate"] = self._exc.auth_header
		if getattr(self._exc, "wait", None):
			headers["Retry-After"] = f"{self._exc.wait}"
		return headers


def custom_exception_handler(exc, context):
	if isinstance(exc, Throttled):
		set_rollback()
		return CustomThrottled(exc).build_response()
	return exception_handler(exc, context)
