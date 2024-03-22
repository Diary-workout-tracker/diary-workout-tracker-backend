from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe

from .managers import CustomUserManager

GENDER_CHOICES = (
	("M", "Male"),
	("F", "Female"),
)


class User(AbstractUser):
	"""Модель пользователя."""

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ()
	username = None

	email = models.EmailField(_("Адрес электронной почты"), unique=True, max_length=254)
	name = models.CharField(_("Полное имя"), max_length=150, null=True, blank=True)
	password = models.CharField(_("Пароль"), max_length=128, null=True)
	gender = models.CharField(_("Пол"), max_length=2, choices=GENDER_CHOICES, blank=True, null=True)
	height_cm = models.PositiveSmallIntegerField(_("Рост в см"), null=True, blank=True)
	weight_kg = models.FloatField(_("Вес в кг"), null=True, blank=True)
	last_completed_training_number = models.PositiveSmallIntegerField(_("Последняя завершенная тренировка"), default=0)
	amount_of_skips = models.PositiveSmallIntegerField(_("Количество доступных пропусков/заморозок"), default=5)
	avatar = models.ImageField(_("Аватар"), upload_to="avatars/", null=True, blank=True)
	objects = CustomUserManager()

	class Meta:
		verbose_name = _("пользователь")
		verbose_name_plural = _("пользователи")

	def __str__(self) -> str:
		return self.email

	def avatar_display(self):
		"""Вывод аватарки для админки."""
		if self.avatar:
			return mark_safe(f'<img src="{self.avatar.url}" width="100" />')
