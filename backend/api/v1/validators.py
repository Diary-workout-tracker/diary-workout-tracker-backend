from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator


class CustomUniqueValidator(UniqueValidator):
	message = _("Такой email уже существует.")
