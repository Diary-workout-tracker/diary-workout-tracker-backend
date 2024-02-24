from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
	"""Serializer for the custom User model."""

	email = serializers.EmailField()

	class Meta:
		model = User
		fields = "__all__"
