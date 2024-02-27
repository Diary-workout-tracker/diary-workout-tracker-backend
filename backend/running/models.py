from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Day(models.Model):
	"""Модель, представляющая день в плане тренировок."""

	day_number = models.PositiveSmallIntegerField(
		primary_key=True,
		verbose_name=_("Номер дня"),
		help_text=_("Номер дня."),
		db_comment=_("Уникальный номер дня в программе тренировок."),
	)
	motivation_phrase = models.CharField(  # XXX: будут ли совпадать с другими или индивидуальны
		verbose_name=_("Мотивационная фраза"),
		max_length=150,
		help_text=_("Мотивационная фраза"),
		db_comment=_("Мотивационная фраза на дне тренеровки."),
	)
	workout = models.JSONField(
		verbose_name=_("Этапы тренеровки"),
		help_text=_("Описанные этапы тренеровки в json."),
		db_comment=_("Описанные этапы тренеровки"),
	)
	workout_info = models.CharField(
		verbose_name=_("Описание тренеровки"),
		max_length=100,
		help_text=_("Описание тренеровки."),
		db_comment=_("Описание тренеровки дополнительно к этапам"),
	)

	class Meta:
		verbose_name = _("День")
		verbose_name_plural = _("Дни")

	def __str__(self) -> str:
		return f"{_('День')} {self.day_number}"


class Achievement(models.Model):
	"""Модель, представляющая достижения."""

	icon = models.ImageField(
		verbose_name=_("Иконка достижения"),
		upload_to="achievement_icons/",
		db_comment=_("Название достижения."),
		help_text=_("Иконка, представляющая достижение."),
	)
	title = models.CharField(
		verbose_name=_("Название достижения"),
		max_length=100,
		help_text=_("Название достижения."),
		db_comment=_("Название достижения."),
	)
	description = models.TextField(
		verbose_name=_("Описание достижения"),
		help_text=_("Описание достижения."),
		db_comment=_("Описание достижения."),
	)
	stars = models.PositiveSmallIntegerField(
		verbose_name=_("Звездность"),
		help_text=_("Уровень выполненного достижения."),
		db_comment=_("Числовое представление уровня сложности достижения."),
	)
	reward_points = models.PositiveSmallIntegerField(
		verbose_name=_("Заморозк"),
		default=1,
		help_text=_("Количество заморозок за достижение."),
		db_comment=_("Количество заморозок за достижение."),
	)

	class Meta:
		ordering = ("title", "stars")
		verbose_name = _("Достижение")
		verbose_name_plural = _("Достижения")
		unique_together = ("title", "stars")

	def __str__(self) -> str:
		return f"{self.title} - {self.stars}"


class UserAchievement(models.Model):
	"""Модель, представляющая связь достижений с пользователем."""

	achievement_date = models.DateTimeField(
		verbose_name=_("Дата получения достижения"),
		auto_now_add=True,
		help_text=_("Дата, когда пользователь получил достижение."),
		db_comment=_("Дата, когда пользователь получил достижение."),
	)
	user_id = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name=_("Пользователь"),
		related_name="user_achievements",
		help_text=_("Пользователь, который получил достижение."),
		db_comment=_("Пользователь, который получил достижение."),
		null=False,
		blank=False,
	)
	achievement_id = models.ForeignKey(
		Achievement,
		on_delete=models.CASCADE,
		verbose_name=_("Достижение"),
		related_name="user_achievements",
		help_text=_("Достижение, полученное пользователем."),
		db_comment=_("Достижение, полученное пользователем."),
		null=False,
		blank=False,
	)

	class Meta:
		verbose_name = _("Достижение пользователя")
		verbose_name_plural = _("Достижения пользователей")

	def __str__(self) -> str:
		return f"{self.user_id.username} - {self.achievement_id.title}"


class History(models.Model):
	"""Модель, представляющая записанную тренеровку."""

	training_date = models.DateTimeField(
		verbose_name=_("Дата тренировки"),
		help_text=_("Дата и время проведения тренировки."),
		db_comment=_("Дата, когда пользователь получил достижение."),
	)
	completed = models.BooleanField(  # XXX: нужен ли, если в конце тренеровки данные
		default=False,
		verbose_name=_("Завершено"),
		help_text=_("Показывает, завершена ли тренировка или нет."),
		db_comment=_("Флаг, указывающий, завершена ли тренировка или нет."),
	)
	training_day = models.ForeignKey(
		Day,
		on_delete=models.CASCADE,
		verbose_name=_("День тренировки"),
		related_name="historis",
		help_text=_("День тренировки."),
		db_comment=_("День, к которому относится тренировка."),
		null=False,
		blank=False,
	)
	route = models.TimeField(
		verbose_name=_("Маршрут"),
		help_text=_("Маршрут тренировки."),
		db_comment=_("Маршрут тренировки."),
	)
	distance = models.PositiveSmallIntegerField(
		verbose_name=_("Дистанция (в метрах)"),
		help_text=_("Пройденная дистанция в метрах."),
		db_comment=_("Пройденная дистанция в метрах."),
	)
	max_speed = models.PositiveSmallIntegerField(
		verbose_name=_("Максимальная скорость"),
		help_text=_("Максимальная достигнутая скорость во время тренировки."),
		db_comment=_("Максимальная достигнутая скорость во время тренировки."),
	)
	avg_speed = models.PositiveSmallIntegerField(
		verbose_name=_("Средняя скорость"),
		help_text=_("Средняя скорость за всю тренировку."),
		db_comment=_("Средняя скорость за всю тренировку."),
	)

	class Meta:
		ordering = ("training_date",)
		verbose_name = _("Тренировка ")
		verbose_name_plural = _("Тренировки")

	def __str__(self) -> str:
		return f"{_('Тренировка')} {self.id}"
