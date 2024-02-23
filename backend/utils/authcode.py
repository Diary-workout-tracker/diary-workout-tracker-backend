from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()


class AuthCode:
	def __init__(self, user) -> None:
		if not isinstance(user, User):
			raise ValidationError(f"{user} is not a User instance")
		self._user = user

	def create_code(self) -> None:
		self._store_code(self._generate_code())

	@property
	def code_is_valid(self, code: int) -> bool:
		pass

	def _generate_code(self):
		pass

	def _store_code(self):
		pass
