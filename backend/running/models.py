from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class MotivationalPhrase(models.Model):
	"""Модель, представляющая мотивационные фразы и фразы отдыха."""

	text = models.TextField(
		verbose_name=_("Текст фразы"),
		help_text=_("Текст фразы."),
		db_comment=_("Текст фразы."),
	)
	rest = models.BooleanField(
		default=False,
		verbose_name=_("Флаг фразы отдыха"),
		help_text=_("Флаг, обозначающий фразу отдыха."),
		db_comment=_("Флаг, обозначающий фразу отдыха."),
	)

	class Meta:
		verbose_name = _("Мотивационная фраза")
		verbose_name_plural = _("Мотивационные фразы")

	def __str__(self):
		return f"{self.text} - {self.rest}"


class Day(models.Model):
	"""Модель, представляющая день в плане тренировок."""

	day_number = models.PositiveSmallIntegerField(
		primary_key=True,
		verbose_name=_("Номер дня"),
		help_text=_("Номер дня."),
		db_comment=_("Уникальный номер дня в программе тренировок."),
	)
	workout = models.JSONField(
		verbose_name=_("Этапы тренировки"),
		help_text=_("Описанные этапы тренировки в json."),
		db_comment=_("Описанные этапы тренировки"),
	)
	workout_info = models.CharField(
		verbose_name=_("Описание тренировки"),
		max_length=200,
		help_text=_("Описание тренировки."),
		db_comment=_("Описание тренировки дополнительно к этапам"),
	)

	class Meta:
		verbose_name = _("День тренировки")
		verbose_name_plural = _("Дни тренировки")

	def __str__(self) -> str:
		return f"{_('День тренировки')} {self.day_number}"


class Achievement(models.Model):
	"""Модель, представляющая достижения."""

	id = models.PositiveBigIntegerField(primary_key=True)
	icon = models.ImageField(
		verbose_name=_("Иконка достижения"),
		upload_to="achievement_icons/",
		db_comment=_("Иконка достижения."),
		help_text=_("Иконка, представляющая достижение."),
	)
	black_white_icon = models.ImageField(
		verbose_name=_("ЧБ иконка достижения"),
		upload_to="achievement_icons/",
		db_comment=_("ЧБ иконка достижения."),
		help_text=_("ЧБ иконка, представляющая достижение."),
	)
	title = models.CharField(
		verbose_name=_("Название достижения"),
		max_length=100,
		help_text=_("Название достижения."),
		db_comment=_("Название достижения."),
		unique=True,
	)
	description = models.TextField(
		verbose_name=_("Описание достижения"),
		help_text=_("Описание достижения."),
		db_comment=_("Описание достижения."),
	)
	reward_points = models.PositiveSmallIntegerField(
		verbose_name=_("Заморозка"),
		default=0,
		help_text=_("Количество заморозок за достижение."),
		db_comment=_("Количество заморозок за достижение."),
	)

	class Meta:
		ordering = ("title",)
		verbose_name = _("Достижение")
		verbose_name_plural = _("Достижения")

	def __str__(self) -> str:
		return self.title


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
	"""Модель, отображающая историю тренировки."""

	training_start = models.DateTimeField(
		verbose_name=_("Время начала тренировки"),
		help_text=_("Дата и время начала тренировки."),
		db_comment=_("Дата и время начала тренировки."),
	)
	training_end = models.DateTimeField(
		verbose_name=_("Время окончания тренировки"),
		help_text=_("Дата и время окончания тренировки."),
		db_comment=_("Дата и время окончания тренировки."),
	)
	completed = models.BooleanField(
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
	image = models.ImageField(
		verbose_name=_("Изображение маршрута"),
		upload_to="history_images/",
		db_comment=_("Изображение пройденного маршрута на карте."),
		help_text=_("Изображение пройденного маршрута на карте."),
		blank=True,
		null=True,
	)
	motivation_phrase = models.CharField(
		verbose_name=_("Мотивационная фраза"),
		max_length=150,
		help_text=_("Мотивационная фраза"),
		db_comment=_("Мотивационная фраза на дне тренировки."),
	)
	cities = ArrayField(
		models.CharField(max_length=150),
		verbose_name=_("Города"),
		help_text=_("Города, в которых были совершены тренировки."),
		db_comment=_("Города, в которых были совершены тренировки."),
	)
	route = models.JSONField(
		verbose_name=_("Маршрут"),
		help_text=_("Маршрут тренировки."),
		db_comment=_("Маршрут тренировки."),
		blank=True,
		null=True,
	)
	distance = models.FloatField(
		verbose_name=_("Дистанция (в метрах)"),
		help_text=_("Пройденная дистанция в метрах."),
		db_comment=_("Пройденная дистанция в метрах."),
	)
	max_speed = models.FloatField(
		verbose_name=_("Максимальная скорость"),
		help_text=_("Максимальная достигнутая скорость во время тренировки."),
		db_comment=_("Максимальная достигнутая скорость во время тренировки."),
	)
	avg_speed = models.FloatField(
		verbose_name=_("Средняя скорость"),
		help_text=_("Средняя скорость за всю тренировку."),
		db_comment=_("Средняя скорость за всю тренировку."),
	)
	height_difference = models.PositiveSmallIntegerField(
		verbose_name=_("Перепад высот"),
		help_text=_("Перепад высот."),
		db_comment=_("Перепад высот."),
	)
	user_id = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name=_("Пользователь"),
		related_name="user_history",
		help_text=_("История пользователя."),
		db_comment=_("История пользователя."),
		null=False,
		blank=False,
	)

	class Meta:
		ordering = ("training_end",)
		verbose_name = _("История тренировки")
		verbose_name_plural = _("История тренировок")

	def __str__(self) -> str:
		return f"{_('История тренировки')} {self.id}"
