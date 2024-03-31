from collections import OrderedDict

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from running.models import Achievement, Day, History, MotivationalPhrase
from users.constants import GENDER_CHOICES
from users.models import User as ClassUser
from utils.authcode import AuthCode
from utils.users import get_user_by_email_or_404

from .constants import FORMAT_DATE, FORMAT_TIME, FORMAT_DATETIME
from .fields import Base64ImageField
from .validators import CustomUniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	"""Сериализатор кастомного пользователя."""

	email = serializers.EmailField(validators=(CustomUniqueValidator(queryset=User.objects.all()),))
	name = serializers.CharField(required=False)
	gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
	height_cm = serializers.IntegerField(allow_null=True, required=False)
	weight_kg = serializers.FloatField(allow_null=True, required=False)
	last_completed_training = serializers.IntegerField(
		source="last_completed_training.training_day.day_number", read_only=True
	)
	date_last_skips = serializers.DateTimeField(required=False)
	amount_of_skips = serializers.IntegerField(required=False)
	avatar = Base64ImageField(allow_null=True, required=False)
	timezone = serializers.CharField(required=False)

	class Meta:
		model = User
		fields = (
			"email",
			"name",
			"gender",
			"height_cm",
			"weight_kg",
			"last_completed_training",
			"date_last_skips",
			"amount_of_skips",
			"avatar",
			"timezone",
		)

	def create(self, validated_data: dict) -> ClassUser:
		"""Создаёт нового пользователя."""
		avatar_data = validated_data.pop("avatar", None)
		user = User.objects.create(**validated_data)
		if avatar_data:
			user.avatar.save(avatar_data.name, avatar_data)
		return user

	def update(self, instance: ClassUser, validated_data: dict) -> ClassUser:
		"""Обновляет данные пользователя."""
		if not validated_data.get("avatar") and (
			"avatar" in validated_data.keys()
			or not self.context["request"].user.avatar
			or self.context["request"].user.avatar in ("avatars/women.png", "avatars/men.png")
		):
			gender = None
			if validated_data.get("gender"):
				gender = validated_data.get("gender")
			elif self.context["request"].user.gender:
				gender = self.context["request"].user.gender
			validated_data["avatar"] = "avatars/women.png" if gender == "F" else "avatars/men.png"

		return super().update(instance, validated_data)


class CustomTokenObtainSerializer(serializers.Serializer):
	email = serializers.EmailField(write_only=True)
	code = serializers.CharField(min_length=4, max_length=4, write_only=True)

	def validate(self, attrs):
		user = get_user_by_email_or_404(attrs["email"])
		authcode = AuthCode(user)
		if authcode.code_is_valid(attrs["code"]):
			return attrs
		raise serializers.ValidationError({"code": ["Неверный или устаревший код"]})

	def create(self, validated_data):
		user = User.objects.get(email=validated_data["email"])

		refresh = RefreshToken.for_user(user)
		return {
			"refresh": str(refresh),
			"access": str(refresh.access_token),
		}


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

	achievement_date = serializers.DateTimeField(format=FORMAT_DATE)
	received = serializers.BooleanField()
	icon = Base64ImageField()

	class Meta:
		model = Achievement
		fields = (
			"id",
			"icon",
			"title",
			"description",
			"reward_points",
			"achievement_date",
			"received",
		)


class AchievementEndTrainingSerializer(serializers.ModelSerializer):
	"""Сериализатор достижения конца тренировки."""

	icon = Base64ImageField()

	class Meta:
		model = Achievement
		fields = (
			"icon",
			"title",
		)


class HistorySerializer(serializers.ModelSerializer):
	"""Сериализатор историй тренировок."""

	image = Base64ImageField(required=False)
	time = serializers.SerializerMethodField(read_only=True)
	achievements = serializers.ListField(required=False, write_only=True, child=serializers.IntegerField())

	class Meta:
		model = History
		fields = (
			"training_start",
			"training_end",
			"training_day",
			"image",
			"motivation_phrase",
			"cities",
			"route",
			"distance",
			"time",
			"max_speed",
			"avg_speed",
			"height_difference",
			"achievements",
		)
		extra_kwargs = {
			"training_end": {"write_only": True},
			"training_day": {"write_only": True},
			"cities": {"write_only": True},
			"max_speed": {"write_only": True, "min_value": 0},
			"distance": {"min_value": 0},
			"avg_speed": {"min_value": 0},
			"route": {"required": False},
		}

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		training_start = instance.training_start
		representation["training_start"] = [
			training_start.strftime(FORMAT_DATE),
			training_start.strftime(FORMAT_DATETIME),
		]
		return representation

	def validate(self, data: OrderedDict) -> OrderedDict:
		if data["training_start"] >= data["training_end"]:
			raise serializers.ValidationError(
				{"training_start_training_end": ["Время начала тренировки должно быть раньше конца"]}
			)
		return data

	def validate_motivation_phrase(self, value: str) -> str:
		if not MotivationalPhrase.objects.filter(text=value).exists():
			raise serializers.ValidationError("Данной мотивационной фразы не существует")
		return value

	def validate_achievements(self, value: list) -> list:
		if value and len(value) > Achievement.objects.filter(id__in=value).count():
			raise serializers.ValidationError({"achievements": ["Некорректные ачивки"]})
		return value

	def get_time(self, obj: History) -> int:
		"""Отдаёт продолжительность тренировки."""
		time_training = obj.training_end - obj.training_start
		minutes = int(time_training.total_seconds() // 60)
		seconds = int(time_training.total_seconds() % 60)
		return FORMAT_TIME.format(minutes, seconds)

	def create(self, validated_data: dict) -> History:
		validated_data["user_id"] = self.context["request"].user
		return super().create(validated_data)
