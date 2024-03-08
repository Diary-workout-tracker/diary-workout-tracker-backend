from freezegun import freeze_time
from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model

from running.models import Day, MotivationalPhrase, RecreationPhrase, History  # noqa
from backend.utils.motivation_phrase import get_rest_phrases, get_dynamic_list_motivation_phrase


User = get_user_model()


@pytest.fixture
def training():
	training = []
	for i in range(1, 101):
		training.append(
			Day(
				day_number=i,
				workout=(
					f'{{"workout":[{{"duration": {i}, "pace": "бег"}}, {{"duration": {i * 2}, "pace": "ходьба"}}]}}'
				),
				workout_info="Тестовое описание",
			)
		)
	return Day.objects.bulk_create(training)


@pytest.fixture
def create_motivation_phrase():
	motivational_phrase = []
	recreation_phrase = []
	for i in range(1, 101):
		if i <= 32:
			recreation_phrase.append(RecreationPhrase(text=f"Фраза отдыха {i}"))
		motivational_phrase.append(MotivationalPhrase(text=f"Мотивационная фраза {i}"))
	RecreationPhrase.objects.bulk_create(recreation_phrase)
	MotivationalPhrase.objects.bulk_create(motivational_phrase)


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def more_five_history(user, training):
	history = []

	for i in range(1, 6):
		history.append(
			History(
				training_date=datetime.now() - timedelta(days=8 - i),
				completed=True,
				training_day=training[i - 1],
				motivation_phrase="Тестовая фраза",
				route="[]",
				distance=1,
				max_speed=1,
				avg_speed=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def more_five_history_last_training_morning(user, training):
	history = []

	for i in range(1, 8):
		history.append(
			History(
				training_date=datetime.now() - timedelta(days=8 - i),
				completed=True,
				training_day=training[i - 1],
				motivation_phrase="Тестовая фраза",
				route="[]",
				distance=1,
				max_speed=1,
				avg_speed=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def four_history(user, training):
	history = []

	for i in range(1, 5):
		history.append(
			History(
				training_date=datetime.now() - timedelta(days=8 - i),
				completed=True,
				training_day=training[i - 1],
				motivation_phrase="Тестовая фраза",
				route="[]",
				distance=1,
				max_speed=1,
				avg_speed=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.fixture
@freeze_time("2024-03-04 00:00:00")
def one_hundred_history(user, training):
	history = []

	for i in range(1, 101):
		history.append(
			History(
				training_date=datetime.now() - timedelta(days=101 - i),
				completed=True,
				training_day=training[i - 1],
				motivation_phrase="Тестовая фраза",
				route="[]",
				distance=1,
				max_speed=1,
				avg_speed=1,
				user_id=user,
			)
		)
	return History.objects.bulk_create(history)


@pytest.mark.django_db
@pytest.mark.parametrize(
	"days_to_replace, rest_phrases",
	(
		((1, 4, 9), ["Фраза отдыха 1", "Фраза отдыха 2", "Фраза отдыха 3"]),
		((1, 2, 3), ["Фраза отдыха 1", "Фраза отдыха 2", "Фраза отдыха 3"]),
		((98, 99, 100), ["Фраза отдыха 31", "Фраза отдыха 32", "Фраза отдыха 1"]),
		((102, 105, 120), ["Фраза отдыха 32", "Фраза отдыха 1", "Фраза отдыха 2"]),
	),
)
def test_get_rest_phrases(create_motivation_phrase, days_to_replace: tuple, rest_phrases: list):
	assert rest_phrases == get_rest_phrases(days_to_replace)


@pytest.mark.django_db
@pytest.mark.parametrize(
	"days_to_replace, error", ((("1", "4", "9"), TypeError), ((-1, -4, -9), ValueError), ((), IndexError))
)
def test_get_rest_phrases_with_strings(create_motivation_phrase, days_to_replace: tuple, error: Exception):
	with pytest.raises(error):
		get_rest_phrases(days_to_replace)


@pytest.mark.django_db
@freeze_time("2024-03-08 00:00:00")
def test_get_dynamic_list_motivation_phrase_more_five_history_morning_day_friday(
	create_motivation_phrase, more_five_history
):
	user = more_five_history[0].user_id
	user.last_completed_training_number = more_five_history[-1].id
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert ("Фраза отдыха 2", "Мотивационная фраза 8", "Мотивационная фраза 10") == (
		motivation_phrase[5],
		motivation_phrase[7],
		motivation_phrase[9],
	)


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_more_five_history(create_motivation_phrase, more_five_history):
	user = more_five_history[0].user_id
	user.last_completed_training_number = more_five_history[-1].id
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert ("Фраза отдыха 2", "Фраза отдыха 3", "Фраза отдыха 4") == (
		motivation_phrase[5],
		motivation_phrase[7],
		motivation_phrase[9],
	)


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_one_hundred_history(create_motivation_phrase, one_hundred_history):
	user = one_hundred_history[0].user_id
	user.last_completed_training_number = one_hundred_history[-1].id
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert motivation_phrase == list(MotivationalPhrase.objects.all().values_list("text", flat=True))


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_four_history(create_motivation_phrase, four_history):
	user = four_history[0].user_id
	user.last_completed_training_number = four_history[-1].id
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert (
		"Фраза отдыха 2",
		"Фраза отдыха 3",
	) == (
		motivation_phrase[6],
		motivation_phrase[9],
	)


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_get_dynamic_list_motivation_phrase_more_five_history_last_training_morning(
	create_motivation_phrase, more_five_history_last_training_morning
):
	user = more_five_history_last_training_morning[0].user_id
	user.last_completed_training_number = more_five_history_last_training_morning[-1].id
	motivation_phrase = get_dynamic_list_motivation_phrase(user)
	assert ("Фраза отдыха 3", "Фраза отдыха 4", "Фраза отдыха 5") == (
		motivation_phrase[7],
		motivation_phrase[9],
		motivation_phrase[11],
	)
