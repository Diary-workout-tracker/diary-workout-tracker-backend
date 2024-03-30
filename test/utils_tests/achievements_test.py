from datetime import timedelta

import pytest
from django.utils import timezone

from backend.utils.achievements import traveler
from running.models import Day, History  # noqa


@pytest.fixture
def history(user):
	return History.objects.create(
		training_start=timezone.localtime(),
		training_end=timezone.localtime() + timedelta(days=1),
		training_day=Day.objects.get(day_number=50),
		motivation_phrase="Тестовая фраза",
		cities=["St. Petersburg"],
		distance=1,
		max_speed=1,
		avg_speed=1,
		height_difference=1,
		user_id=user,
	)


@pytest.mark.django_db
def test_user_1_cities_per_training(user, history):
	user.last_completed_training = history
	user.save()
	assert traveler(user) is False


@pytest.mark.django_db
def test_user_3_cities_per_training(user, history):
	history.cities = ["Moscow", "St. Petersburg", "Karaganda"]
	history.save()
	user.last_completed_training = history
	user.save()
	assert traveler(user) is True
