from datetime import timedelta
from functools import partial

import pytz
from django.db import transaction
from django.utils import timezone

from running.models import Achievement, History, UserAchievement
from users.models import User
from utils.constants import IOS_ACHIEVEMENTS


def tourist(user: User, history: History = None) -> bool:
	"""Проверка достижения Турист."""
	if history.training_day.day_number == 1:
		return False
	city_last_training = set(history.cities)
	city_first_training = set(History.objects.filter(user_id=user).order_by("training_start").first().cities)
	return not city_last_training.issubset(city_first_training)


def traveler(user: User, history: History = None) -> bool:
	"""Проверка достижения Путешественник."""
	if history is None:
		return False
	return len(set(history.cities)) >= 3


def equator(user: User, history: History = None) -> bool:
	"""Проверка достижения Экватор"""

	if history is None:
		return False
	return history.training_day.day_number == 50


def get_count_training_current_week(user: User) -> int:
	"""Возвращает количество пройденных тренировок на текущей неделе."""
	date_now = timezone.localtime(timezone=pytz.timezone(user.timezone))
	date_now_number_day_week = date_now.weekday()
	date_start_current_week = (date_now - timedelta(days=date_now_number_day_week)).replace(
		hour=0, minute=0, second=0, microsecond=0
	)
	return History.objects.filter(user_id=user, training_start__range=[date_start_current_week, date_now]).count()


def persistent(user: User, history: History) -> bool:
	"""Проверка достижения Упорный."""
	return get_count_training_current_week(user) == 4


def machine(user: User, history: History) -> bool:
	"""Проверка достижения Машина."""

	return get_count_training_current_week(user) == 5


def validate_n_km_club(km_club_amount: int, user: User, history: History = None) -> bool:
	"""Проверка достижений клуб N километров."""

	return user.total_m_run // 1000 >= km_club_amount


def n_km_club(km_club_amount: int) -> callable:
	"""Используем partial, чтобы не плодить кучу одинаковых ф-ций."""

	return partial(validate_n_km_club, km_club_amount=km_club_amount)


def validate_goblet(amount_of_trainings: int, user: User, history: History = None) -> bool:
	if not history:
		return False
	return history.training_day.day_number >= amount_of_trainings


def goblet(amount_of_trainings: int) -> callable:
	"""Валидатор достижения кубок со звездами."""

	return partial(validate_goblet, amount_of_trainings=amount_of_trainings)


VALIDATORS = {
	1: persistent,  # Упорный
	2: machine,  # Машина
	3: equator,  # Экватор
	4: n_km_club(20),  # Клуб N км.
	5: n_km_club(50),
	6: n_km_club(100),
	7: n_km_club(150),
	8: n_km_club(200),
	9: n_km_club(300),
	10: n_km_club(500),
	11: n_km_club(1000),
	12: goblet(3),  # Кубок со звездами - 1, 3 тренировки
	13: goblet(10),
	14: goblet(30),
	15: goblet(50),
	16: goblet(70),
	17: goblet(100),  # Большой кубок со звездами - 100 тренировок
	21: tourist,  # Турист
	22: traveler,  # Путешественник
}


class AchievementUpdater:
	"""По пользователю и данным из запроса обновляет достижения.
	Проверяет по списку валидаторов для всех незавершенных ачивок,
	если находит новую выполненную, добавляет в список. Обновляет базу.
	Метод (свойство) new_achievements вызванный после update_achievements()
	вернет список свежеполученных ачивок для дальнейшей десериализации.
	"""

	def __init__(self, user, ios_achievements: list[int] = None, history: History = None) -> None:
		self._user = user
		self._history = history
		self._new_achievements = []
		self._unfinished_achievements = None
		self._new_ios_achievements = None
		if ios_achievements and isinstance(ios_achievements, list):
			self._new_ios_achievements = list(
				Achievement.objects.filter(
					id__in=[_id for _id in map(int, ios_achievements) if _id in IOS_ACHIEVEMENTS]
				)
			)

	def update_achievements(self):
		self._query_unfinished_achievements()
		self._check_for_new_backend_achievements()
		self._check_for_new_ios_achievements()
		self._update_database()

	def _update_database(self):
		"""Обновляем БД по списку новых ачивок.
		Логика следующая:
		        - для одноразовых ачивок создается запись в UserAchievement
		        - для многоразовых ачивок если записи нет, создается, если есть, пересоздается."""

		if not self._new_achievements:
			return
		user_achievements = [
			UserAchievement(user_id=self._user, achievement_id=achievement) for achievement in self._new_achievements
		]
		rewards = sum(
			[achievement.reward_points for achievement in self._new_achievements]
		)  # XXX: проверить и прорефакторить
		self._user.amount_of_skips += rewards
		with transaction.atomic():
			if rewards > 0:
				self._user.save()
			UserAchievement.objects.filter(
				user_id=self._user, achievement_id__in=self._new_achievements, achievement_id__recurring=True
			).delete()
			UserAchievement.objects.bulk_create(user_achievements)

	def _check_for_new_backend_achievements(self):
		"""Проверка на выполнение достижений"""

		for achievement in self._unfinished_achievements:
			validator = VALIDATORS.get(achievement.id)
			if validator is not None and validator(user=self._user, history=self._history):
				self._new_achievements.append(achievement)

	def _check_for_new_ios_achievements(self):
		"""Добавление внешних достиженией"""
		if self._new_ios_achievements is not None:
			self._new_achievements.extend(self._new_ios_achievements)

	def _query_unfinished_achievements(self):
		"""Извлечение неполученных ачивок"""

		non_ios_achievements = Achievement.objects.exclude(id__in=IOS_ACHIEVEMENTS).prefetch_related(
			"user_achievements"
		)
		recurring_non_ios = non_ios_achievements.filter(recurring=True)
		unfinished_non_ios = non_ios_achievements.exclude(
			id__in=UserAchievement.objects.filter(user_id=self._user.id).values("achievement_id")
		)
		self._unfinished_achievements = unfinished_non_ios | recurring_non_ios

	@property
	def unfinished_achievements(self):
		return self._unfinished_achievements

	@property
	def new_achievements(self):
		"""Полный список свежих ачивок для десериализации."""

		return self._new_achievements
