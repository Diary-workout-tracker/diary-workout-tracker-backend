import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create(email="test@test.ru", name="Tester John")


@pytest.fixture
def user_client(user):
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
