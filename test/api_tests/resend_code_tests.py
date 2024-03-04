import pytest
from django.urls import reverse
from rest_framework import status

URL = reverse("code-resend")


@pytest.mark.django_db
def test_code_for_registered_user_is_sent(client, user):
	response = client.post(URL, {"email": user.email}, format="json")
	assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_code_for_unregistered_user_is_not_sent(client):
	response = client.post(URL, {"email": "test@me.myfriend"}, format="json")
	assert response.status_code == status.HTTP_404_NOT_FOUND
