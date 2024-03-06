import pytest
from django.urls import reverse
from rest_framework import status

NAME = "achievement"


@pytest.mark.django_db
def test_all_achievments_returns_correct(user_client, achievements) -> None:
	"""Тестирование выдачи списка достижений"""
	response = user_client.get(reverse(NAME + "-list"))
	assert response.status_code == status.HTTP_200_OK
	assert len(response.data) == 3
	for item, eqil in zip(sorted(response.data, key=lambda x: x["id"]), achievements):
		assert item["id"] == eqil.id
		assert item["title"] == eqil.title
		assert item["description"] == eqil.description
		assert item["reward_points"] == eqil.reward_points


@pytest.mark.django_db
def test_achievment_returns_correct(user_client, achievements) -> None:
	"""Тестирование выдачи информации о достижение"""
	achievement = achievements[0]
	response = user_client.get(reverse(NAME + "-detail", kwargs={"pk": achievement.id}))
	assert response.status_code == status.HTTP_200_OK
	assert response.data["id"] == achievement.id
	assert response.data["title"] == achievement.title
	assert response.data["description"] == achievement.description
	assert response.data["reward_points"] == achievement.reward_points


@pytest.mark.django_db
def test_me_achievment_returns_correct(user_client, achievement_to_user) -> None:
	"""Тестирование выдачи списка достижений авторизированного пользователя"""
	response = user_client.get(
		reverse(
			NAME + "-me",
		)
	)
	achievement = response.data[0]["achievement_id"]
	assert response.status_code == status.HTTP_200_OK
	assert len(response.data) == 1
	assert achievement["id"] == achievement_to_user.achievement_id.id
	assert achievement["title"] == achievement_to_user.achievement_id.title
	assert achievement["description"] == achievement_to_user.achievement_id.description
	assert achievement["reward_points"] == achievement_to_user.achievement_id.reward_points
	assert response.data[0]["achievement_date"] is not None
