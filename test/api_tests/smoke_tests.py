from django.urls import reverse
from rest_framework import status


def test_health_check_works(client):
	response = client.get(reverse("health"))
	assert response.status_code == status.HTTP_200_OK
	assert response.data == {"Health": "OK"}
