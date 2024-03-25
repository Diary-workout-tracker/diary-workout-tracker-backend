from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from backend.utils import authcode

from ..utils_tests.authcode_tests import DummyMailSend

User = get_user_model()
URL = reverse("token-refresh")


def get_authcode_for_user(_user):
	sender = DummyMailSend()
	auth_code = authcode.AuthCode(_user)
	auth_code.set_sender(sender)
	auth_code.create_code()
	return sender.code


@pytest.fixture
def throttling_num_requests_patch():
	"""Функция нужна, чтобы обойти троттлинг в тестах при генерации кода.
	Тестов много, поэтому при стандартных настройках троттлинга тесты проходят не все.
	"""

	settings.ACCESS_RESTORE_CODE_THROTTLING = {
		"duration": timedelta(milliseconds=100),
		"num_requests": 10,
		"cooldown": timedelta(milliseconds=100),
	}


@pytest.fixture
def get_users_token(client, user):
	payload = {"email": user.email, "code": get_authcode_for_user(user)}
	return client.post(URL, payload, format="json")


@pytest.mark.django_db
def test_correct_code_yields_token(get_users_token):
	response = get_users_token
	assert response.status_code == status.HTTP_200_OK
	assert "refresh" in response.data
	assert "access" in response.data
	assert response.data["refresh"] != ""
	assert response.data["access"] != ""


@pytest.mark.django_db
def test_incorrect_code_yields_exception(client, user, throttling_num_requests_patch):
	payload = {"email": user.email, "code": "abcx"}
	response = client.post(URL, payload, format="json")
	assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_received_token_specifies_correct_user(get_users_token, user):
	token = get_users_token.data["access"]
	decoded_token = AccessToken(token)
	user_id_from_token = decoded_token["user_id"]
	assert user_id_from_token == user.id
