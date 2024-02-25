from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from utils.authcode import AuthCode

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
	"""Serializer for the custom User model."""

	email = serializers.EmailField(validators=(UniqueValidator(queryset=User.objects.all()),))

	class Meta:
		model = User
		fields = ("email", "name")


class CustomTokenObtainSerializer(serializers.Serializer):
	email = serializers.EmailField(write_only=True)
	code = serializers.CharField(min_length=4, max_length=4, write_only=True)

	def create(self, validated_data):
		email = validated_data["email"]
		code = validated_data["code"]

		user = get_object_or_404(User, email=email)
		authcode = AuthCode(user)
		if authcode.code_is_valid(code):
			refresh = RefreshToken.for_user(user)
			return {
				"refresh": str(refresh),
				"access": str(refresh.access_token),
			}
		else:
			raise serializers.ValidationError({"detail": "Invalid or expired code"})
