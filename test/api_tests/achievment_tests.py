from collections import OrderedDict

import pytest
from django.urls import reverse
from rest_framework import status

from running.models import Achievement

NAME = "achievement"


def check_achievement_data(data: OrderedDict, achievement: Achievement) -> None:
	"""Тестирование соответствие полей достижения"""
	assert data["id"] == achievement.id
	assert data["title"] == achievement.title
	assert data["description"] == achievement.description
	assert data["reward_points"] == achievement.reward_points


@pytest.mark.django_db
def test_all_achievments_returns_correct(user_client, achievements) -> None:
	"""Тестирование выдачи списка достижений"""
	response = user_client.get(reverse(NAME + "-list"))
	assert response.status_code == status.HTTP_200_OK
	assert len(response.data) == 3
	for item, equal in zip(sorted(response.data, key=lambda x: x["id"]), achievements):
		check_achievement_data(item, equal)


@pytest.mark.django_db
def test_achievment_returns_correct(user_client, achievements) -> None:
	"""Тестирование выдачи информации о достижение"""
	achievement = achievements[0]
	response = user_client.get(reverse(NAME + "-detail", kwargs={"pk": achievement.id}))
	assert response.status_code == status.HTTP_200_OK
	check_achievement_data(response.data, achievement)


@pytest.mark.django_db
def test_me_achievment_returns_correct(user_client, achievement_to_user) -> None:
	"""Тестирование выдачи списка достижений авторизированного пользователя"""
	response = user_client.get(reverse(NAME + "-me"))
	assert response.status_code == status.HTTP_200_OK
	assert len(response.data) == 1
	data = response.data[0]
	achievement = data["achievement_id"]
	check_achievement_data(achievement, achievement_to_user.achievement_id)
	assert data is not None
