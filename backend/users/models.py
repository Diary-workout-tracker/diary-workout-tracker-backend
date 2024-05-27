from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from .constants import (
	DEFAULT_AMOUNT_OF_SKIPS,
	GENDER_CHOICES,
	MAX_LEN_EMAIL,
	MAX_LEN_GENDER,
	MAX_LEN_NAME,
	MAX_LEN_PASSWORD,
	MAX_LEN_TIMEZONE,
)
from .managers import CustomUserManager


class User(AbstractUser):
	"""Модель пользователя."""

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ()
	username = None

	email = models.EmailField(_("Адрес электронной почты"), unique=True, max_length=MAX_LEN_EMAIL)
	name = models.CharField(_("Полное имя"), max_length=MAX_LEN_NAME, null=True, blank=True)
	password = models.CharField(_("Пароль"), max_length=MAX_LEN_PASSWORD, null=True)
	gender = models.CharField(_("Пол"), max_length=MAX_LEN_GENDER, choices=GENDER_CHOICES, blank=True, null=True)
	height_cm = models.PositiveSmallIntegerField(_("Рост в см"), null=True, blank=True)
	weight_kg = models.FloatField(_("Вес в кг"), null=True, blank=True)
	last_completed_training = models.ForeignKey(
		"running.History",
		on_delete=models.SET_NULL,
		verbose_name=_("Последняя завершенная тренировка"),
		null=True,
		blank=True,
	)
	date_last_skips = models.DateTimeField(_("Дата последнего пропуска"), null=True, blank=True)
	amount_of_skips = models.PositiveSmallIntegerField(
		_("Количество доступных пропусков/заморозок"), default=DEFAULT_AMOUNT_OF_SKIPS
	)
	avatar = models.ImageField(_("Аватар"), upload_to="avatars/", null=True, blank=True)
	total_m_run = models.FloatField(_("Всего пробежал метров"), default=0)
	timezone = models.CharField(_("Часовой пояс пользователя"), max_length=MAX_LEN_TIMEZONE, null=True, blank=True)
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
