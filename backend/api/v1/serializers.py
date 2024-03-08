from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import GENDER_CHOICES
from running.models import Day
from utils.authcode import AuthCode

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	"""Сериализатор кастомного пользователя."""

	email = serializers.EmailField(validators=(UniqueValidator(queryset=User.objects.all()),))
	name = serializers.CharField(required=False)
	gender = serializers.ChoiceField(choices=GENDER_CHOICES, allow_blank=True, required=False)
	height_cm = serializers.IntegerField(allow_null=True, required=False)
	weight_kg = serializers.FloatField(allow_null=True, required=False)
	last_completed_training_number = serializers.IntegerField(read_only=True)
	amount_of_skips = serializers.IntegerField(read_only=True)

	class Meta:
		model = User
		fields = (
			"email",
			"name",
			"gender",
			"height_cm",
			"weight_kg",
			"last_completed_training_number",
			"amount_of_skips",
		)


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
			raise serializers.ValidationError({"detail": "Неверный или устаревший код"})


class TrainingSerializer(serializers.ModelSerializer):
	"""Сериализатор тренировок."""

	motivation_phrase = serializers.CharField()
	completed = serializers.BooleanField(required=False)

	class Meta:
		model = Day
		fields = ("day_number", "workout", "workout_info", "motivation_phrase", "completed")
