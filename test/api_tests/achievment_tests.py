import pytest
import pytz
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from backend.api.v1.constants import FORMAT_DATE
from running.models import UserAchievement  # noqa

User = get_user_model()


@pytest.mark.django_db
def test_all_achievments_returns_correct(user_client, achievements) -> None:
	"""Тестирование выдачи списка достижений"""
	date = timezone.localtime()
	user = User.objects.get(email="test@test.ru")
	UserAchievement.objects.create(achievement_date=date, user_id=user, achievement_id=achievements[0])
	response = user_client.get(reverse("achievements"))
	assert response.status_code == status.HTTP_200_OK
	assert len(response.data) == 3
	achievement = response.data[0]
	assert achievement["achievement_date"] == date.astimezone(pytz.timezone(user.timezone)).strftime(FORMAT_DATE)
	assert achievement["received"] is not None
