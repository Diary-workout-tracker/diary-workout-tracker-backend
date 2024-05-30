from datetime import datetime, timedelta

import pytz

from users.models import User


def get_date_activity(user: User, user_timezone: str) -> datetime:
	"""Отдаёт дату последней активности в виде тренировки или заморозки."""
	date_activity: datetime = max(
		[date for date in [user.date_last_skips, user.last_completed_training.training_start] if date is not None]
	)
	return date_activity.astimezone(pytz.timezone(user_timezone))


def counts_missed_days(user: User, user_timezone: str, now: datetime) -> tuple[int, datetime, int]:
	"""
	Просчитывает кол-во пропущенных дней и возвращает:
	    пропущенные дни, дату день назад, кол-во заморозок пользователя
	"""
	date_activity = get_date_activity(user, user_timezone)
	amount_of_skips = user.amount_of_skips
	date_day_ago = now - timedelta(days=1)
	days_missed = (date_day_ago.date() - date_activity.date()).days
	return days_missed, date_day_ago, amount_of_skips
