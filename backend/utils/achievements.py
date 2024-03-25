from running.models import Achievement, UserAchievement
from users.models import User


# def equator(x): return x.user_history.last().training_day == 50
# валидаторы ачивок. могут быть и лямбдами, и обычными функциями, возвращают для пользователя булево значение - выполнена ли ачивка
def equator(x):
	return True


def traveler(user: User) -> bool:
	"""Проверка достижения Путешественник."""
	last_training = user.user_history.last()
	return len(set(last_training.cities)) >= 3


def persistent(x):
	return True


VALIDATORS = {
	"Экватор": equator,
	"уПоРный": persistent,
	"Путешественник": traveler,
}

VALIDATORS = {key.lower(): value for key, value in VALIDATORS.items()}


class AchievementUpdater:
	"""По пользователю и данным из запроса обновляет достижения.
	Проверяет по списку валидаторов для всех незавершенных ачивок,
	если находит новую выполненную, добавляет в список. Обновляет базу.
	Метод (свойство) new_achievements вызванный после update_achievements()
	вернет список свежеполученных ачивок для дальнейшей десериализации.
	"""

	def __init__(self, user, data) -> None:
		self._user = user
		self._data = data
		self._new_achievements = []
		self._unfinished_achievements = None

	def update_achievements(self):
		self._query_unfinished_achievements()
		self._check_for_new_backend_achievements()
		self._check_for_new_ios_achievements()
		self._update_database()

	def _update_database(self):
		if not self._new_achievements:
			return
		user_achievements = [
			UserAchievement(user_id=self._user, achievement_id=achievement) for achievement in self._new_achievements
		]
		UserAchievement.objects.bulk_create(user_achievements)

	def _check_for_new_backend_achievements(self):
		for achievement in self._unfinished_achievements:
			validator = VALIDATORS.get(achievement.title.lower())
			if validator is not None and validator(self._user) is True:
				self._new_achievements.append(achievement)

	def _check_for_new_ios_achievements(self):
		ios_achievements = self._data.get("achievements")
		if ios_achievements is not None:
			# при условии, что по этому ключу будет список с id-шнниками новых иос-ачивок. Если будут названия, надо написать сравнение с названиями из query
			self._new_achievements.extend(ios_achievements)

	def _query_unfinished_achievements(self):
		self._unfinished_achievements = Achievement.objects.exclude(
			id__in=UserAchievement.objects.filter(user_id=self._user.id).values("achievement_id")
		)

	@property
	def new_achievements(self):
		"""Полный список свежих ачивок для десериализации."""

		return self._new_achievements
