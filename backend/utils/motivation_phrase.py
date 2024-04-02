from datetime import timedelta
import pytz

from django.db.models.query import QuerySet
from django.utils import timezone

from running.models import History, MotivationalPhrase
from users.models import User


def get_count_training_last_week(user: User) -> int:
	"""Возвращает кол-во тренировок на прошлой неделе."""
	date_now = timezone.localtime(timezone=pytz.timezone(user.timezone)).replace(
		hour=0, minute=0, second=0, microsecond=0
	)
	date_now_number_day_week = date_now.weekday() + 1
	date_end_last_week = date_now - timedelta(days=date_now_number_day_week)
	date_start_last_week = date_end_last_week - timedelta(days=6)
	date_end_last_week += timedelta(hours=23, minutes=59, seconds=59)
	return History.objects.filter(
		user_id=user, training_start__range=[date_start_last_week, date_end_last_week]
	).count()


def get_rest_phrases_to_replace(rest_phrases: list, days_to_replace: tuple) -> QuerySet:
	"""Отдаёт фразы отдыха для замены."""
	phrase_count = len(rest_phrases)
	replacement_phrases = []
	index = int(days_to_replace[0] // (100 / (phrase_count - 1)))
	for i in range(len(days_to_replace)):
		replacement_phrases.append(rest_phrases[index])
		index = (index + 1) % phrase_count
	return replacement_phrases


def get_phrases() -> tuple:
	"""Отдаёт фразы отдыха и мотивации."""
	phrases = MotivationalPhrase.objects.all()
	motivational_phrases = []
	rest_phrases = []
	for phrase in phrases:
		if phrase.rest:
			rest_phrases.append(phrase.text)
			continue
		motivational_phrases.append(phrase.text)
	return motivational_phrases, rest_phrases


def replaces_phrases(motivational_phrases: list, days_to_replace: tuple, rest_phrases: list) -> None:
	"""Заменяет мотивационные фразы на фразы отдыха."""
	for i in range(len(days_to_replace)):
		if days_to_replace[i] >= 100:
			return
		motivational_phrases[days_to_replace[i]] = rest_phrases[i]


def get_dynamic_list_motivation_phrase(user: User) -> list:
	"""Формирует динамический список мотивационных фраз
	в зависимости от истории тренировок."""
	motivational_phrases, rest_phrases = get_phrases()
	last_training = user.last_completed_training
	if not last_training:
		return motivational_phrases
	count_training = get_count_training_last_week(user)
	if count_training < 4:
		return motivational_phrases
	date_now_number_day_week = timezone.localtime(timezone=pytz.timezone(user.timezone)).weekday() + 1
	day_last_training = last_training.training_day.day_number
	if count_training == 4:
		shift_wednesday = 3 - date_now_number_day_week
		shift_saturday = 6 - date_now_number_day_week
		if shift_wednesday >= 0 and shift_saturday >= 0:
			days_to_replace = (day_last_training + shift_wednesday, day_last_training + shift_saturday)
			replacement_phrases = get_rest_phrases_to_replace(rest_phrases, days_to_replace)
			replaces_phrases(motivational_phrases, days_to_replace, replacement_phrases)
		elif shift_saturday >= 0:
			days_to_replace = (day_last_training + shift_saturday,)
			replacement_phrases = get_rest_phrases_to_replace(rest_phrases, days_to_replace)
			replaces_phrases(motivational_phrases, days_to_replace, replacement_phrases)
		return motivational_phrases

	shift_first_rest = 1 - date_now_number_day_week
	shift_second_rest = 3 - date_now_number_day_week
	shift_third_rest = 5 - date_now_number_day_week
	date_last_training_week = last_training.training_start.weekday() + 1
	if date_last_training_week == 7:
		shift_first_rest += 1
		shift_second_rest += 1
		shift_third_rest += 1
	if shift_first_rest >= 0 and shift_second_rest >= 0 and shift_third_rest >= 0:
		days_to_replace = (
			day_last_training + shift_first_rest,
			day_last_training + shift_second_rest,
			day_last_training + shift_third_rest,
		)
		replacement_phrases = get_rest_phrases_to_replace(rest_phrases, days_to_replace)
		replaces_phrases(motivational_phrases, days_to_replace, replacement_phrases)
	elif shift_second_rest >= 0 and shift_third_rest >= 0:
		days_to_replace = (day_last_training + shift_second_rest, day_last_training + shift_third_rest)
		replacement_phrases = get_rest_phrases_to_replace(rest_phrases, days_to_replace)
		replaces_phrases(motivational_phrases, days_to_replace, replacement_phrases)
	elif shift_third_rest >= 0:
		days_to_replace = (day_last_training + shift_third_rest,)
		replacement_phrases = get_rest_phrases_to_replace(rest_phrases, days_to_replace)
		replaces_phrases(motivational_phrases, days_to_replace, replacement_phrases)
	return motivational_phrases
