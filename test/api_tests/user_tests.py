# TODO когда будет готов список обязательных полей для регистрации, сделать тесты на успех регистрации
# TODO когда все обязательные поля заполнены, неуспех - если хотя бы одного из них нет, корректность
# TODO заполнения модели данными из полей при регистрации.


from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


def user_register_post_response(payload):
    client = APIClient()
    return client.post(reverse("user-register"), payload, format="json")


@pytest.mark.django_db
def test_user_is_registered():
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
    response = user_register_post_response({"email": incorrect_email})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_cannot_register_if_a_user_already_exists(client):
    payload = {"email": "test@testuser.com"}
    User.objects.create(email=payload["email"])
    response = user_register_post_response(payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
