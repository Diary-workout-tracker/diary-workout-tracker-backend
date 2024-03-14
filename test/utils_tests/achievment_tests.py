from django.utils import timezone
from freezegun import freeze_time
import pytest

from backend.utils.achievement import designation_received_achievements
from running.models import Achievement, UserAchievement  # noqa


@pytest.mark.django_db
@freeze_time("2024-03-04 00:00:00")
def test_designation_received_achievements(user, achievements) -> None:
	date = timezone.now().date()
	UserAchievement.objects.create(achievement_date=date, user_id=user, achievement_id=achievements[0])
	user_achievement = UserAchievement.objects.filter(user_id=user)
	achievement = Achievement.objects.all()
	designation_received_achievements(achievement, user_achievement)
	assert achievement[0].received
	assert achievement[0].achievement_date.date() == date
