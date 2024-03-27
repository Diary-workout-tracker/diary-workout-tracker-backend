from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

User = get_user_model()


def get_user_by_email_or_404(email):
	try:
		return User.objects.get(email=email)
	except User.DoesNotExist:
		raise NotFound(detail={"email": ["Пользователь с таким email не найден"]})
