from django.db.models.query import QuerySet

from .utils import binary_search


def designation_received_achievements(achievement: QuerySet, user_achievement: QuerySet) -> None:
	"""Помечает полученые достижения пользователем."""
	for element in user_achievement:
		find_element = element.achievement_id
		index = binary_search(achievement, find_element)
		achievement[index].received = True
		achievement[index].achievement_date = element.achievement_date
