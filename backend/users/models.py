from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager


class User(AbstractUser):
	"""Custom User model."""

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ()
	username = None
	email = models.EmailField("email address", unique=True, max_length=254)
	name = models.CharField("full name", max_length=150, default="Бегун 1")
	password = models.CharField("password", max_length=128, null=True)
	last_completed_training_number = models.PositiveSmallIntegerField("last completed training", default=0)
	amount_of_skips = models.PositiveSmallIntegerField("last completed training", default=0)

	objects = CustomUserManager()

	class Meta:
		verbose_name = "user"
		verbose_name_plural = "users"

	def __str__(self) -> str:
		return self.email
