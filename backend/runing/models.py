from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Day(models.Model):
	day_number = models.PositiveSmallIntegerField(  # XXX: уточнить будут ли разные тренеровки
		primary_key=True, verbose_name=_("Номер дня"), db_comment=_("Уникальный номер дня в программе тренировок.")
	)
	motivation_phrase = models.CharField(  # XXX: будут ли совпадать с другими или индивидуальны
		verbose_name=_("Мотивационная фраза"), max_length=255, db_comment=_("Мотивационная фраза на дне тренеровки.")
	)
	training_info = models.CharField(  # TODO: придумать разбиение, а то как учитывать
		verbose_name=_("Описание тренировки"), max_length=255, db_comment=_("Краткое описание содержания тренировки.")
	)
	training_time = models.IntegerField(verbose_name=_("Время тренировки"))  # TODO: время же
	temp = models.CharField(
		verbose_name=_("Темп тренировки"),
		max_length=255,
	)  # TODO: это что "с включением 5 минут ускорений (интервалы)"

	class Meta:
		verbose_name = _("День")
		verbose_name_plural = _("Дни")

	def __str__(self):
		return f"{_('День')} {self.day_number}"


class Achievement(models.Model):
	icon = models.ImageField(
		verbose_name=_("Иконка достижения"),
		upload_to="achievement_icons/",
		help_text=_("Иконка, представляющая достижение."),
	)
	name = models.CharField(
		verbose_name=_("Название достижения"),
		max_length=255,
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
		ordering = ("name", "stars")
		verbose_name = _("Достижение")
		verbose_name_plural = _("Достижения")
		unique_together = ("name", "stars")

	def __str__(self):
		return f"{self.name} - {self.difficulty_level}"


class UserAchievement(models.Model):
	achievement_date = models.DateTimeField(
		verbose_name=_("Дата получения достижения"),
		auto_now_add=True,
		help_text=_("Дата, когда пользователь получил достижение."),
		db_comment=_("Дата, когда пользователь получил достижение."),
	)
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name=_("Пользователь"),
		help_text=_("Пользователь, который получил достижение."),
		db_comment=_("Пользователь, который получил достижение."),
	)
	achievement = models.ForeignKey(
		Achievement,
		on_delete=models.CASCADE,
		verbose_name=_("Достижение"),
		help_text=_("Достижение, полученное пользователем."),
		db_comment=_("Достижение, полученное пользователем."),
	)

	class Meta:
		verbose_name = _("Достижение пользователя")
		verbose_name_plural = _("Достижения пользователей")

	def __str__(self):
		return f"{self.user.username} - {self.achievement.name}"


class Training(models.Model):
	training_date = models.DateTimeField(
		verbose_name=_("Дата тренировки"),
		help_text=_("Дата и время проведения тренировки."),
		db_comment=_("Дата, когда пользователь получил достижение."),
	)
	completed = models.BooleanField(  # XXX: нужен ли
		default=False,
		verbose_name=_("Завершено"),
		help_text=_("Показывает, завершена ли тренировка или нет."),
		db_comment=_("Флаг, указывающий, завершена ли тренировка или нет."),
	)
	training_day = models.ForeignKey(
		Day,
		on_delete=models.CASCADE,
		verbose_name=_("День тренировки"),
		help_text=_("День, к которому относится тренировка."),
		db_comment=_("День, к которому относится тренировка."),
	)
	route = models.CharField(
		max_length=255,
		verbose_name=_("Маршрут"),
		help_text=_("Маршрут тренировки."),
		db_comment=_("Маршрут тренировки."),
	)
	distance = models.IntegerField(
		verbose_name=_("Дистанция (в метрах)"),
		help_text=_("Пройденная дистанция в метрах."),
		db_comment=_("Пройденная дистанция в метрах."),
	)
	max_speed = models.IntegerField(
		verbose_name=_("Максимальная скорость"),
		help_text=_("Максимальная достигнутая скорость во время тренировки."),
		db_comment=_("Максимальная достигнутая скорость во время тренировки."),
	)
	avg_speed = models.IntegerField(
		verbose_name=_("Средняя скорость"),
		help_text=_("Средняя скорость за всю тренировку."),
		db_comment=_("Средняя скорость за всю тренировку."),
	)
	# calories = models.IntegerField(
	#     verbose_name=_('Калории'),
	#     help_text=_('Количество сожженных калорий во время тренировки.'),
	#     db_comment=_('Количество сожженных калорий во время тренировки.')
	# )
	# avg_puls = models.IntegerField(
	#     verbose_name=_('Средний пульс'),
	#     help_text=_('Средний пульс во время тренировки.'),
	#     db_comment=_('Средний пульс во время тренировки.')
	# )
	# height_difference = models.IntegerField(
	#     verbose_name=_('Перепад высот'),
	#     help_text=_('Разница в высоте во время тренировки.'),
	#     db_comment=_('Разница в высоте во время тренировки.')
	# )

	class Meta:
		ordering = ("training_date",)
		verbose_name = _("Тренировка ")
		verbose_name_plural = _("Тренировки")

	def __str__(self):
		return f"{_('Тренировка')} {self.id}"
