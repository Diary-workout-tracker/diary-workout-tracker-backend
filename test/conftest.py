import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create(email="test@test.ru", name="Tester John")
