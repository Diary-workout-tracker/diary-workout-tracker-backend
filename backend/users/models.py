from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager

GENDER_CHOICES = (
	("M", "Male"),
	("F", "Female"),
	("NS", "Not Set"),
)


class User(AbstractUser):
	"""Модель пользователя."""

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ()
	username = None
	email = models.EmailField("Адрес электронной почты", unique=True, max_length=254)
	name = models.CharField("Полное имя", max_length=150)
	password = models.CharField("Пароль", max_length=128, null=True)
	gender = models.CharField("Пол", max_length=2, choices=GENDER_CHOICES, default="NS")
	height_cm = models.PositiveSmallIntegerField("Рост в см", null=True, blank=True)
	weight_kg = models.FloatField("Вес в кг", null=True, blank=True)
	last_completed_training_number = models.PositiveSmallIntegerField("Последняя завершенная тренировка", default=0)
	amount_of_skips = models.PositiveSmallIntegerField("Количество доступных пропусков/заморозок", default=5)

	objects = CustomUserManager()

	class Meta:
		verbose_name = "пользователь"
		verbose_name_plural = "пользователи"

	def __str__(self) -> str:
		return self.email
