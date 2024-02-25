from django.urls import reverse
from rest_framework import status
import pytest
from django.contrib.auth import get_user_model


User = get_user_model()
URL = reverse("me")


def test_my_info_requires_token(client):
    assert client.get(URL).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_endpoint_returns_correct_info(user_client, user):
    response = user_client.get(URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email
    assert response.data["name"] == user.name


@pytest.mark.django_db
def test_my_info_patch_works(user_client, user):
    response = user_client.patch(URL, {"name": "Prince Igor"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.name == "Prince Igor"


@pytest.mark.django_db
def test_my_profile_delete_works(user_client, user):
    assert User.objects.filter(email=user.email).exists()
    response = user_client.delete(URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(email=user.email).exists()
