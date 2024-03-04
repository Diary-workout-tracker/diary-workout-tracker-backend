from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError("Необходимо указать email")
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)

		if extra_fields.get("is_staff") is not True:
			raise ValueError("У суперпользователя должно быть is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("У суперпользователя должно быть is_superuser=True.")

		return self.create_user(email, password, **extra_fields)
