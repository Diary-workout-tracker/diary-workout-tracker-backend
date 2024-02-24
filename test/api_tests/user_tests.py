from rest_framework import status
from django.urls import reverse
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_is_registered(client):
    payload = {"email": "test@testuser.com"}
    response = client.post(reverse("user-register"), payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.last().email == payload["email"]
