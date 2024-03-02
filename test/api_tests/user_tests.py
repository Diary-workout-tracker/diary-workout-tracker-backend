# TODO когда будет готов список обязательных полей для регистрации, сделать тесты на успех регистрации
# TODO когда все обязательные поля заполнены, неуспех - если хотя бы одного из них нет, корректность
# TODO заполнения модели данными из полей при регистрации.


import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from backend.utils import authcode

from ..utils_tests.authcode_tests import DummyMailSend

User = get_user_model()
CLIENT = APIClient()


def user_register_post_response(payload):
	return CLIENT.post(reverse("user-register"), payload, format="json")


@pytest.fixture
def patched_dummy_sender(monkeypatch):
	sender = DummyMailSend()

	def fake_send_auth_code(user) -> None:
		auth_code = authcode.AuthCode(user)
		auth_code.set_sender(sender)
		auth_code.create_code()

	monkeypatch.setattr("api.v1.views.send_auth_code", fake_send_auth_code)
	return sender


@pytest.mark.django_db
def test_user_with_only_email_provided_is_registered():
	payload = {"email": "test@testuser.com"}
	response = user_register_post_response(payload)
	assert response.status_code == status.HTTP_201_CREATED
	assert User.objects.last().email == payload["email"]


@pytest.mark.parametrize(
	"incorrect_email",
	("test#testuser.com", "test@test@test.ru", "test.ru", "שלום@test.ru", "admin"),
)
@pytest.mark.django_db
def test_incorrect_email_doesnt_pass_validation(incorrect_email):
	response = user_register_post_response({"email": incorrect_email, "name": "Shlomo A"})
	assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_cannot_be_registered_without_a_email():
	response = user_register_post_response({"name": "King George IV"})
	assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_cannot_register_if_a_user_already_exists(client):
	payload = {"email": "test@testuser.com"}
	User.objects.create(email=payload["email"])
	response = user_register_post_response(payload)
	assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_email_is_sent_upon_registering(patched_dummy_sender):
	assert patched_dummy_sender.mail_sent is False
	assert patched_dummy_sender.mail_address is None
	payload = {"email": "test@testuser.com", "name": "email tester"}
	user_register_post_response(payload)
	assert patched_dummy_sender.mail_sent is True
	assert patched_dummy_sender.mail_address == payload["email"]


@pytest.mark.django_db
def test_sent_code_is_correct(patched_dummy_sender):
	payload = {"email": "test2@testuser.com", "name": "Code Tester"}
	user_register_post_response(payload)
	registered_user = User.objects.get(email=payload["email"])
	auth_code = authcode.AuthCode(registered_user)
	assert auth_code.code_is_valid(patched_dummy_sender.code)
