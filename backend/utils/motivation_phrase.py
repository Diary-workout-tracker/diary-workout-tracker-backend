from datetime import datetime, timedelta

from django.db.models.query import QuerySet

from running.models import MotivationalPhrase, RecreationPhrase, History
from users.models import User


def get_rest_phrases(days_to_replace: tuple) -> QuerySet:
	"""Отдаёт фразы отдыха."""
	phrase = RecreationPhrase.objects.all()
	phrase_count = len(phrase)
	rest_phrases = []
	index = int(days_to_replace[0] // (100 / (phrase_count - 1)))
	for i in range(len(days_to_replace)):
		rest_phrases.append(phrase[index].text)
		index = (index + 1) % phrase_count
	return rest_phrases


def replaces_phrases(motivational_phrases: list, days_to_replace: tuple, rest_phrases: list) -> None:
	"""Заменяет мотивационные фразы на фразы отдыха."""
	for i in range(len(days_to_replace)):
		if days_to_replace[i] >= 100:
			return
		motivational_phrases[days_to_replace[i]] = rest_phrases[i]


def get_dynamic_list_motivation_phrase(user: User) -> list:
	"""Формирует динамический список мотивационных фраз
	в зависимости от истории тренировок."""
	motivational_phrases = list(MotivationalPhrase.objects.all().values_list("text", flat=True))
	last_completed_training_number = user.last_completed_training_number
	if not last_completed_training_number:
		return motivational_phrases
	date_now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	date_now_number_day_week = date_now.weekday() + 1
	date_end_last_week = date_now - timedelta(days=date_now_number_day_week)
	date_start_last_week = date_end_last_week - timedelta(days=6)
	date_end_last_week += timedelta(hours=23, minutes=59, seconds=59)
	count_training = History.objects.filter(
		user_id=user, completed=True, training_date__range=[date_start_last_week, date_end_last_week]
	).count()
	if count_training < 4:
		return motivational_phrases
	last_training = History.objects.get(id=last_completed_training_number)
	day_last_training = last_training.training_day.day_number
	if count_training == 4:
		shift_wednesday = 3 - date_now_number_day_week
		shift_saturday = 6 - date_now_number_day_week
		if shift_wednesday >= 0 and shift_saturday >= 0:
			days_to_replace = (day_last_training + shift_wednesday, day_last_training + shift_saturday)
			rest_phrases = get_rest_phrases(days_to_replace)
			replaces_phrases(motivational_phrases, days_to_replace, rest_phrases)
		elif shift_saturday >= 0:
			days_to_replace = (day_last_training + shift_saturday,)
			rest_phrases = get_rest_phrases(days_to_replace)
			replaces_phrases(motivational_phrases, days_to_replace, rest_phrases)
		return motivational_phrases

	shift_first_rest = 1 - date_now_number_day_week
	shift_second_rest = 3 - date_now_number_day_week
	shift_third_rest = 5 - date_now_number_day_week
	date_last_training_week = last_training.training_date.weekday() + 1
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
		rest_phrases = get_rest_phrases(days_to_replace)
		replaces_phrases(motivational_phrases, days_to_replace, rest_phrases)
	elif shift_second_rest >= 0 and shift_third_rest >= 0:
		days_to_replace = (day_last_training + shift_second_rest, day_last_training + shift_third_rest)
		rest_phrases = get_rest_phrases(days_to_replace)
		replaces_phrases(motivational_phrases, days_to_replace, rest_phrases)
	elif shift_third_rest >= 0:
		days_to_replace = (day_last_training + shift_third_rest,)
		rest_phrases = get_rest_phrases(days_to_replace)
		replaces_phrases(motivational_phrases, days_to_replace, rest_phrases)
	return motivational_phrases
