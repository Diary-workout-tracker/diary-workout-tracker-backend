from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from running.models import UserAchievement  # noqa

User = get_user_model()
url = reverse("history")


@pytest.fixture
def training_end_data():
	return {
		"training_start": "2024-10-11T14:30:00",
		"training_end": "2024-10-11T15:31:00",
		"training_day": 1,
		"cities": ["Питер", "Волгоград"],
		"distance": 66600,
		"max_speed": 121,
		"avg_speed": 11,
		"height_difference": 5,
		"motivation_phrase": "Отдых – это не конец тренировки, это начало новых возможностей.",
	}


def user_achievement_count_by_id(user, _id):
	return UserAchievement.objects.filter(user_id=user.id, achievement_id=_id).count()


def add_1_day_to_str(date: str) -> str:
	return (datetime.fromisoformat(date) + timedelta(days=1)).isoformat()


@pytest.mark.django_db
def test_ios_achievement_is_being_created(user, user_client, load_achievement_fixtures, training_end_data) -> None:
	assert user_achievement_count_by_id(user, 26) == 0  # 26 == АфтерДарк
	training_end_data["achievements"] = [26]
	response = user_client.post(url, training_end_data, format="json")
	assert response.status_code == status.HTTP_201_CREATED
	assert user_achievement_count_by_id(user, 26) == 1


@pytest.mark.django_db
def test_ios_achievement_works_with_str(user, user_client, load_achievement_fixtures, training_end_data) -> None:
	training_end_data["achievements"] = ["26"]
	response = user_client.post(url, training_end_data, format="json")
	assert response.status_code == status.HTTP_201_CREATED
	assert user_achievement_count_by_id(user, 26) == 1


@pytest.mark.django_db
def test_non_ios_achievement_is_not_created(user, user_client, load_achievement_fixtures, training_end_data) -> None:
	assert user_achievement_count_by_id(user, 11) == 0  # 11 == Клуб 1000 км
	training_end_data["achievements"] = [11]
	user_client.post(url, training_end_data, format="json")
	assert user_achievement_count_by_id(user, 11) == 0


@pytest.mark.django_db
def test_recurring_ios_achievement_is_not_duplicated(user, user_client, load_achievement_fixtures, training_end_data):
	assert user_achievement_count_by_id(user, 26) == 0
	training_end_data["achievements"] = [26]
	for _ in range(2):
		response = user_client.post(url, training_end_data, format="json")
		training_end_data["training_day"] += 1
		training_end_data["training_start"] = add_1_day_to_str(training_end_data["training_start"])
		training_end_data["training_end"] = add_1_day_to_str(training_end_data["training_end"])
		assert response.status_code == status.HTTP_201_CREATED
	assert user_achievement_count_by_id(user, 26) == 1


@pytest.mark.django_db
def test_recurring_non_ios_achievement_is_not_duplicated(
	user, user_client, load_achievement_fixtures, training_end_data
):
	assert user_achievement_count_by_id(user, 21) == 0  # Турист
	training_end_data["achievements"] = []
	for i in range(5):
		response = user_client.post(url, training_end_data, format="json")
		training_end_data["cities"] = [str(i)]
		training_end_data["training_day"] += 1
		training_end_data["training_start"] = add_1_day_to_str(training_end_data["training_start"])
		training_end_data["training_end"] = add_1_day_to_str(training_end_data["training_end"])
		assert response.status_code == status.HTTP_201_CREATED
	assert user_achievement_count_by_id(user, 21) == 1
