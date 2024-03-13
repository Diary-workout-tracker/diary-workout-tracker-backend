import base64
import datetime

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from constants.achievment import FORMAT_DATE
from running.models import Achievement
from users.models import GENDER_CHOICES
from running.models import Day
from utils.authcode import AuthCode

User = get_user_model()


class Base64ImageField(serializers.ImageField):
	"""Класс для сериализации изображения и десериализации URI."""

	def to_internal_value(self, data):
		"""Декодирование base64 в файл."""

		if isinstance(data, str) and data.startswith("data:image"):
			format, imgstr = data.split(";base64,")
			ext = format.split("/")[-1]
			data = ContentFile(
				base64.b64decode(imgstr),
				name=str(datetime.datetime.now().timestamp()) + "." + ext,
			)
		return super().to_internal_value(data)

	def to_representation(self, value):
		"""Возвращает полный url изображения."""

		return self.context["request"].build_absolute_uri(value.url)


class UserSerializer(serializers.ModelSerializer):
	"""Сериализатор кастомного пользователя."""

	email = serializers.EmailField(validators=(UniqueValidator(queryset=User.objects.all()),))
	name = serializers.CharField(required=False)
	gender = serializers.ChoiceField(choices=GENDER_CHOICES, allow_blank=True, required=False)
	height_cm = serializers.IntegerField(allow_null=True, required=False)
	weight_kg = serializers.FloatField(allow_null=True, required=False)
	last_completed_training_number = serializers.IntegerField(read_only=True)
	amount_of_skips = serializers.IntegerField(read_only=True)
	avatar = Base64ImageField(required=False)

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
			"avatar",
		)

	def create(self, validated_data):
		avatar_data = validated_data.pop("avatar", None)
		user = User.objects.create(**validated_data)
		if avatar_data:
			user.avatar.save(avatar_data.name, avatar_data)
		return user


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
		fields = (
			"day_number",
			"workout",
			"workout_info",
			"motivation_phrase",
			"completed",
		)


class AchievementSerializer(serializers.ModelSerializer):
	"""Сериализатор достижения."""

	achievement_date = serializers.DateTimeField(format=FORMAT_DATE, required=False)
	received = serializers.BooleanField(required=False)

	class Meta:
		model = Achievement
		fields = (
			"icon",
			"title",
			"description",
			"reward_points",
			"achievement_date",
			"received",
		)
