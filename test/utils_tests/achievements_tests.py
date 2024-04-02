from datetime import timedelta

import pytest
from django.utils import timezone

from backend.utils.achievements import AchievementUpdater, equator, n_km_club, tourist, traveler
from backend.utils.constants import IOS_ACHIEVEMENTS
from running.models import Achievement, Day, History, UserAchievement  # noqa


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


@pytest.fixture
def history_first(user):
	return History.objects.create(
		training_start=timezone.localtime() - timedelta(days=11),
		training_end=timezone.localtime() - timedelta(days=10),
		training_day=Day.objects.get(day_number=1),
		motivation_phrase="Тестовая фраза",
		cities=["St. Petersburg"],
		distance=1,
		max_speed=1,
		avg_speed=1,
		height_difference=1,
		user_id=user,
	)


def achievement_by_id(_id: int):
	return Achievement.objects.get(id=_id)


@pytest.mark.django_db
def test_user_last_day_is_50(user, history):
	assert equator(user) is True


@pytest.mark.django_db
def test_user_training_day_is_not_50(user, history):
	history.training_day = Day.objects.get(day_number=30)
	history.save()
	assert equator(user) is False


@pytest.mark.django_db
def test_all_km_achievements_are_received_on_single_big_distance(user, history_first, load_achievement_fixtures):
	km_achievement_ids = 4, 5, 6, 7, 8, 9, 10, 11
	user.total_m_run = 1_000_000
	user.last_completed_training = history_first
	user.save()
	updater = AchievementUpdater(user, {})
	for km_achievement_id in km_achievement_ids:
		assert Achievement(id=km_achievement_id) not in updater.new_achievements
	updater.update_achievements()
	for km_achievement_id in km_achievement_ids:
		assert Achievement(id=km_achievement_id) in updater.new_achievements


@pytest.mark.parametrize("total_km_run", (20, 50, 100, 150, 200, 300, 500, 1000))
@pytest.mark.django_db
def test_n_km_club_validator(user, total_km_run):
	user.total_m_run = total_km_run * 1000 - 1
	user.save()
	assert n_km_club(km_club_amount=total_km_run)(user=user) is False
	user.total_m_run = total_km_run * 1000
	user.save()
	assert n_km_club(km_club_amount=total_km_run)(user=user) is True


@pytest.mark.django_db
def test_all_goblet_achievements_are_received_on_last_training(history, history_first, user, load_achievement_fixtures):
	goblet_achievement_ids = 12, 13, 14, 15, 16, 17
	history.training_day = Day.objects.get(day_number=100)
	history.save()
	user.last_completed_training = history
	user.save()
	updater = AchievementUpdater(user, {})
	for km_achievement_id in goblet_achievement_ids:
		assert Achievement(id=km_achievement_id) not in updater.new_achievements
	updater.update_achievements()
	for km_achievement_id in goblet_achievement_ids:
		assert Achievement(id=km_achievement_id) in updater.new_achievements


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


@pytest.mark.django_db
def test_tourist_one_history(user, history_first):
	user.last_completed_training = history_first
	user.save()
	assert not tourist(user)


@pytest.mark.django_db
def test_tourist_two_history_completed(user, history, history_first):
	history.cities = ["St. Petersburg", "Moscow"]
	history.save()
	history_first.cities = ["St. Petersburg"]
	history_first.save()
	user.last_completed_training = history
	user.save()
	assert tourist(user)
	history.cities = ["St. Petersburg"]
	history.save()
	history_first.cities = ["Tula"]
	history_first.save()
	assert tourist(user)
	history.cities = ["St. Petersburg", "Tula"]
	history.save()
	history_first.cities = ["St. Petersburg", "Moscow"]
	history_first.save()
	assert tourist(user)


@pytest.mark.django_db
def test_tourist_two_history_not_completed(user, history, history_first):
	user.last_completed_training = history
	user.save()
	assert not tourist(user)
	history.cities = ["St. Petersburg"]
	history.save()
	history_first.cities = ["St. Petersburg", "Moscow"]
	history_first.save()
	assert not tourist(user)


@pytest.mark.django_db
def test_query_returns_correct_achievements(history, user, load_achievement_fixtures):
	"""Проверяет, что query вернет правильные ачивки для дальнейшей проверки.
	А именно:
	- в query не будет iOS-ачивок,
	- разовые будут только в том случае, если они еще не выполнены,
	- многократные - будут даже если они уже есть в выполненых.
	"""

	user.last_completed_training = history
	user.save()
	updater = AchievementUpdater(user)
	updater._query_unfinished_achievements()
	assert len(updater.unfinished_achievements) == len(Achievement.objects.all()) - len(IOS_ACHIEVEMENTS)
	for ios_achievement_id in IOS_ACHIEVEMENTS:
		assert Achievement.objects.get(id=ios_achievement_id) not in updater.unfinished_achievements
	UserAchievement.objects.create(user_id=user, achievement_id=achievement_by_id(19))  # штормбрейкер recurring_ios
	UserAchievement.objects.create(user_id=user, achievement_id=achievement_by_id(2))  # машина recurring_non_ios
	UserAchievement.objects.create(user_id=user, achievement_id=achievement_by_id(20))  # пионер single_ios
	UserAchievement.objects.create(user_id=user, achievement_id=achievement_by_id(3))  # экватор single_non_ios
	updater._query_unfinished_achievements()
	assert Achievement.objects.get(id=3) not in updater.unfinished_achievements
	assert Achievement.objects.get(id=2) in updater.unfinished_achievements
	assert len(updater.unfinished_achievements) == len(Achievement.objects.all()) - len(IOS_ACHIEVEMENTS) - 1
