import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from running.models import Achievement, UserAchievement

User = get_user_model()


@pytest.fixture
def user():
	return User.objects.create(email="test@test.ru", name="Tester John", timezone="Europe/Moscow")


@pytest.fixture
def user_client(user):
	refresh = RefreshToken.for_user(user)
	token = str(refresh.access_token)
	client = APIClient()
	client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
	return client


@pytest.fixture
def achievements() -> tuple[Achievement]:
	achievement1 = Achievement.objects.create(
		id=1,
		title="One",
		description="One achievement",
		reward_points=1,
	)
	achievement2 = Achievement.objects.create(
		id=2,
		title="Two",
		description="Two achievement",
		reward_points=2,
	)
	achievement3 = Achievement.objects.create(
		id=3,
		title="Three",
		description="Three achievement",
		reward_points=3,
	)
	return achievement1, achievement2, achievement3


@pytest.fixture
def achievement_to_user(user, achievements) -> UserAchievement:
	to_user = UserAchievement.objects.create(
		user_id=user,
		achievement_id=achievements[0],
		achievement_date=timezone.localtime(),
	)
	return to_user
