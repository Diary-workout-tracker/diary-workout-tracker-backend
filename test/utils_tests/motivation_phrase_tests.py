from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time
from running.models import Day, History, MotivationalPhrase  # noqa

from backend.utils.motivation_phrase import (
	get_count_training_last_week,
	get_dynamic_list_motivation_phrase,
	get_phrases,
	get_rest_phrases_to_replace,
	replaces_phrases,
)

User = get_user_model()


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def more_five_history(user):
	history = []

	for i in range(1, 6):
		history.append(
			History(
				training_start=timezone.localtime() - timedelta(days=8 - i),
				training_end=timezone.localtime() - timedelta(days=8 - i),
				training_day=Day.objects.get(day_number=i),
				motivation_phrase="Тестовая фраза",
				cities=["Moscow"],
				distance=1,
				max_speed=1,
				avg_speed=1,
				height_difference=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def more_five_history_last_training_morning(user):
	history = []

	for i in range(1, 8):
		history.append(
			History(
				training_start=timezone.localtime() - timedelta(days=8 - i),
				training_end=timezone.localtime() - timedelta(days=8 - i),
				training_day=Day.objects.get(day_number=i),
				motivation_phrase="Тестовая фраза",
				cities=["Moscow"],
				distance=1,
				max_speed=1,
				avg_speed=1,
				height_difference=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def four_history(user):
	history = []

	for i in range(1, 5):
		history.append(
			History(
				training_start=timezone.localtime() - timedelta(days=8 - i),
				training_end=timezone.localtime() - timedelta(days=8 - i),
				training_day=Day.objects.get(day_number=i),
				motivation_phrase="Тестовая фраза",
				cities=["Moscow"],
				distance=1,
				max_speed=1,
				avg_speed=1,
				height_difference=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def one_hundred_history(user):
	history = []

	for i in range(1, 101):
		history.append(
			History(
				training_start=timezone.localtime() - timedelta(days=101 - i),
				training_end=timezone.localtime() - timedelta(days=101 - i),
				training_day=Day.objects.get(day_number=i),
				motivation_phrase="Тестовая фраза",
				cities=["Moscow"],
				distance=1,
				max_speed=1,
				avg_speed=1,
				height_difference=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.mark.django_db
@pytest.mark.parametrize(
	"days_to_replace, replacement_phrases",
	(
		(
			(1, 4, 9),
			[
				"Отдых – это не лень, это инвестиция в твою следующую победу.",
				"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
				"Отдыхай, когда устал, но не сдавайся.",
			],
		),
		(
			(1, 2, 3),
			[
				"Отдых – это не лень, это инвестиция в твою следующую победу.",
				"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
				"Отдыхай, когда устал, но не сдавайся.",
			],
		),
		(
			(98, 99, 100),
			[
				"Помни, что отдых – это тоже часть твоего тренировочного плана.",
				"Восстановление – это твой путь к более сильной версии себя.",
				"Отдых – это не лень, это инвестиция в твою следующую победу.",
			],
		),
		(
			(102, 105, 120),
			[
				"Восстановление – это твой путь к более сильной версии себя.",
				"Отдых – это не лень, это инвестиция в твою следующую победу.",
				"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
			],
		),
	),
)
def test_get_rest_phrases_to_replace(days_to_replace: tuple, replacement_phrases: list):
	_, rest_phrases = get_phrases()
	assert replacement_phrases == get_rest_phrases_to_replace(rest_phrases, days_to_replace)


@pytest.mark.django_db
@pytest.mark.parametrize("days_to_replace, error", ((("1", "4", "9"), TypeError), ((), IndexError)))
def test_get_rest_phrases_to_replace_with_strings(days_to_replace: tuple, error: Exception):
	_, rest_phrases = get_phrases()
	with pytest.raises(error):
		get_rest_phrases_to_replace(rest_phrases, days_to_replace)


@pytest.mark.django_db
@freeze_time("2024-03-08 00:00:00")
def test_get_dynamic_list_motivation_phrase_more_five_history_morning_day_friday(more_five_history):
	user = more_five_history[0].user_id
	user.last_completed_training = more_five_history[-1]
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert (
		"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
		"Не сравнивай себя с другими, соревнуйся с собой.",
		"Бег – это свобода, которую ты даришь себе.",
	) == (
		motivation_phrase[5],
		motivation_phrase[7],
		motivation_phrase[9],
	)


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_more_five_history(more_five_history):
	user = more_five_history[0].user_id
	user.last_completed_training = more_five_history[-1]
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert (
		"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
		"Отдыхай, когда устал, но не сдавайся.",
		"Отдыхая, ты заряжаешься силой для новых свершений.",
	) == (
		motivation_phrase[5],
		motivation_phrase[7],
		motivation_phrase[9],
	)


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_one_hundred_history(one_hundred_history):
	user = one_hundred_history[0].user_id
	user.last_completed_training = one_hundred_history[-1]
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert motivation_phrase == get_phrases()[0]


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_four_history(four_history):
	user = four_history[0].user_id
	user.last_completed_training = four_history[-1]
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert (
		"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
		"Отдыхай, когда устал, но не сдавайся.",
	) == (
		motivation_phrase[6],
		motivation_phrase[9],
	)


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_more_five_history_last_training_morning(
	more_five_history_last_training_morning,
):
	user = more_five_history_last_training_morning[0].user_id
	user.last_completed_training = more_five_history_last_training_morning[-1]
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert (
		"Отдыхай, когда устал, но не сдавайся.",
		"Отдыхая, ты заряжаешься силой для новых свершений.",
		"В каждом отдыхе – залог новых достижений.",
	) == (
		motivation_phrase[8],
		motivation_phrase[10],
		motivation_phrase[12],
	)


@pytest.mark.django_db
@pytest.mark.parametrize(
	"days_to_replace, rest_phrases",
	(
		(
			(1, 2, 3),
			(
				"Отдых – это не лень, это инвестиция в твою следующую победу.",
				"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
				"Отдыхай, когда устал, но не сдавайся.",
			),
		),
		(
			(1, 2),
			(
				"Отдых – это не лень, это инвестиция в твою следующую победу.",
				"Восстановление – ключ к росту. Дай своему телу то, что ему нужно.",
			),
		),
		((1,), ("Отдых – это не лень, это инвестиция в твою следующую победу.",)),
	),
)
def test_replaces_phrases(days_to_replace, rest_phrases):
	motivational_phrases = get_phrases()[0]
	replaces_phrases(motivational_phrases, days_to_replace, rest_phrases)
	new_motivational_phrases = tuple(motivational_phrases[day] for day in days_to_replace)
	assert new_motivational_phrases == rest_phrases


@pytest.mark.django_db
def test_replaces_phrases_not_index():
	days_to_replace = (99, 100, 101)
	rest_phrases = ("Фраза отдыха 1", "Фраза отдыха 2", "Фраза отдыха 3")
	motivational_phrases = get_phrases()[0]
	replaces_phrases(motivational_phrases, days_to_replace, rest_phrases)
	assert motivational_phrases[days_to_replace[0]] == rest_phrases[0]


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_count_training_last_week(more_five_history):
	user = more_five_history[0].user_id
	assert 5 == get_count_training_last_week(user)


@pytest.mark.django_db
def test_get_phrases():
	motivational_phrases = list(MotivationalPhrase.objects.filter(rest=False).values_list("text", flat=True))
	rest_phrases = list(MotivationalPhrase.objects.filter(rest=True).values_list("text", flat=True))
	assert (motivational_phrases, rest_phrases) == get_phrases()
