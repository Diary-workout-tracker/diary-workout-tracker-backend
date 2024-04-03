import time
from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

URL = reverse("code-resend")
User = get_user_model()


@pytest.fixture
def code_user():
	return User.objects.create(email="code@tester.com")


@pytest.fixture
def alternative_throttling_settings():
	settings.ACCESS_RESTORE_CODE_THROTTLING = {
		"duration": timedelta(milliseconds=300),
		"num_requests": 3,
		"cooldown": timedelta(milliseconds=300),
	}


def request_is_throttled(user, client):
	return client.post(URL, {"email": user.email}, format="json").status_code == status.HTTP_429_TOO_MANY_REQUESTS


def request_is_not_throttled(user, client):
	return client.post(URL, {"email": user.email}, format="json").status_code == status.HTTP_201_CREATED


def check_request_code_after_last_try_returns_error(code_user, client):
	for _ in range(settings.ACCESS_RESTORE_CODE_THROTTLING["num_requests"]):
		assert request_is_not_throttled(code_user, client)
	assert request_is_throttled(code_user, client)


def check_another_user_can_request_code_while_first_user_is_on_a_cooldown(code_user, client, user):
	assert request_is_throttled(code_user, client)
	assert request_is_not_throttled(user, client)
	assert request_is_throttled(code_user, client)


def check_code_user_can_request_code_after_cooldown(code_user, client):
	assert request_is_throttled(code_user, client)
	time.sleep(settings.ACCESS_RESTORE_CODE_THROTTLING["cooldown"].total_seconds())
	assert request_is_not_throttled(code_user, client)


@pytest.mark.django_db
def test_main_throttling_sequence(alternative_throttling_settings, code_user, client, user):
	check_request_code_after_last_try_returns_error(code_user, client)
	check_another_user_can_request_code_while_first_user_is_on_a_cooldown(code_user, client, user)
	check_code_user_can_request_code_after_cooldown(code_user, client)
