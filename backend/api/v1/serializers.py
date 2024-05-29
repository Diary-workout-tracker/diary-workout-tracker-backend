from collections import OrderedDict
from datetime import datetime

import pytz
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from running.models import Achievement, Day, History, MotivationalPhrase
from users.constants import GENDER_CHOICES, MAX_LEN_NAME
from users.models import User as ClassUser
from utils.authcode import AuthCode
from utils.users import get_user_by_email_or_404
from utils.amount_skips import counts_missed_days

from .constants import FORMAT_DATE, FORMAT_DATETIME, FORMAT_TIME
from .fields import Base64ImageField
from .validators import CustomUniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	"""Сериализатор кастомного пользователя."""

	email = serializers.EmailField(validators=(CustomUniqueValidator(queryset=User.objects.all()),))

	class Meta:
		model = User
		fields = ("email",)


class UserTimezoneSerializer(serializers.ModelSerializer):
	"""Сериализатор timezone пользователя."""

	class Meta:
		model = User
		fields = ("timezone",)
		extra_kwargs = {"timezone": {"required": True}}

	def validate_timezone(self, value: str) -> str:
		"""Валидация timezone пользователя."""
		if value in pytz.all_timezones_set:
			return value
		raise serializers.ValidationError("Несуществующая timezone.")


class MeSerializer(serializers.ModelSerializer):
	"""Сериализатор Me пользователя."""

	email = serializers.EmailField(read_only=True)
	name = serializers.CharField(required=False, max_length=MAX_LEN_NAME)
	gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
	height_cm = serializers.IntegerField(min_value=0, max_value=32767, allow_null=True, required=False)
	weight_kg = serializers.FloatField(min_value=0, allow_null=True, required=False)
	last_completed_training = serializers.IntegerField(
		source="last_completed_training.training_day.day_number", read_only=True
	)
	date_last_skips = serializers.DateTimeField(required=False)
	amount_of_skips = serializers.IntegerField(required=False)
	avatar = Base64ImageField(allow_null=True, required=False)

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
		)

	def to_representation(self, instance: ClassUser) -> dict:
		representation = super().to_representation(instance)
		date_last_skips = instance.date_last_skips
		if date_last_skips:
			user_timezone = pytz.timezone(self.context["request"].user.timezone)
			representation["date_last_skips"] = date_last_skips.astimezone(user_timezone).strftime(FORMAT_DATE)
		return representation

	def validate(self, data: OrderedDict) -> OrderedDict:
		date_last_skips = data.get("date_last_skips")
		amount_of_skips = data.get("amount_of_skips")
		if [date_last_skips, amount_of_skips].count(None) == 1:
			raise serializers.ValidationError(
				{"date_last_skips_amount_of_skips": ["Поля должны присутствовать одновременно."]}
			)
		return data

	def validate_amount_of_skips(self, value: int) -> int:
		amount_of_skips = self.context["request"].user.amount_of_skips
		if not amount_of_skips:
			raise serializers.ValidationError("У пользователя отсутсвуют заморозки.")
		new_amount_of_skips = amount_of_skips - 1
		if new_amount_of_skips != value:
			raise serializers.ValidationError(f"Заморозки должны быть равны {new_amount_of_skips}.")
		return value

	def validate_date_last_skips(self, value: datetime) -> datetime:
		user: ClassUser = self.context["request"].user
		date_last_skips = user.date_last_skips
		user_timezone = pytz.timezone(user.timezone)
		localdate = timezone.localdate(timezone=user_timezone)
		user_timezone_value = value.astimezone(user_timezone).date()
		if localdate != user_timezone_value:
			raise serializers.ValidationError("День заморозки должен быть равен текущему дню.")
		if date_last_skips:
			date_last_skips = date_last_skips.astimezone(user_timezone).date()
			if date_last_skips == user_timezone_value:
				raise serializers.ValidationError("Тренировка уже заморожена.")
		return value

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
		raise serializers.ValidationError({"code": ["Неверный или устаревший код."]})

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

	def to_representation(self, instance: Achievement) -> dict:
		representation = super().to_representation(instance)
		achievement_date = instance.achievement_date
		if achievement_date:
			user_timezone = pytz.timezone(self.context["request"].user.timezone)
			representation["achievement_date"] = achievement_date.astimezone(user_timezone).strftime(FORMAT_DATE)
		return representation


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

	def to_representation(self, instance: History) -> dict:
		representation = super().to_representation(instance)
		training_start = instance.training_start
		user = self.context["request"].user
		user_timezone = pytz.timezone(user.timezone)
		representation["training_start"] = [
			training_start.astimezone(user_timezone).strftime(FORMAT_DATE),
			training_start.astimezone(user_timezone).strftime(FORMAT_DATETIME),
		]
		return representation

	def validate(self, data: OrderedDict) -> OrderedDict:
		if data["training_start"] >= data["training_end"]:
			raise serializers.ValidationError(
				{"training_start_training_end": ["Время начала тренировки должно быть раньше конца."]}
			)
		return data

	def _validate_date(self, value: datetime, name_field: str) -> datetime:
		user = self.context["request"].user
		last_completed_training = user.last_completed_training
		user_timezone = pytz.timezone(user.timezone)
		if (
			last_completed_training
			and value.astimezone(user_timezone).date()
			<= getattr(last_completed_training, name_field).astimezone(user_timezone).date()
		):
			raise serializers.ValidationError("Дата должна быть больше прошлой тренировки.")
		return value

	def _check_lock_training(self, value: datetime) -> None:
		"""Проверка блокировки челленджа."""
		user: ClassUser = self.context["request"].user
		if not user.last_completed_training:
			return
		now = value.astimezone(pytz.timezone(user.timezone))
		days_missed, *_ = counts_missed_days(user, user.timezone, now)
		if user.amount_of_skips < days_missed:
			raise serializers.ValidationError("Невозможно сохранить тренировку при заблокированном челлендже.")

	def validate_training_start(self, value: datetime) -> datetime:
		self._check_lock_training(value)
		return self._validate_date(value, "training_start")

	def validate_training_end(self, value: datetime) -> datetime:
		return self._validate_date(value, "training_end")

	def validate_motivation_phrase(self, value: str) -> str:
		if not MotivationalPhrase.objects.filter(text=value).exists():
			raise serializers.ValidationError("Данной мотивационной фразы не существует.")
		return value

	def validate_training_day(self, value: Day) -> Day:
		last_completed_training = self.context["request"].user.last_completed_training
		if last_completed_training:
			day_number_last_training = last_completed_training.training_day.day_number
			if value.day_number - 1 != day_number_last_training:
				raise serializers.ValidationError(f"День тренировки должен быть равен {day_number_last_training+1}.")
		elif value.day_number != 1:
			raise serializers.ValidationError("День тренировки должен быть равен 1.")
		return value

	def validate_achievements(self, value: list) -> list:
		if value and len(value) > Achievement.objects.filter(id__in=value).count():
			raise serializers.ValidationError("Некорректные ачивки.")
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


class ResponseUserDefaultSerializer(serializers.Serializer):
	"""Сериализатор возвращаемого значения UserDefaultView."""

	default = serializers.BooleanField()


class ResponseUpdateSerializer(serializers.Serializer):
	"""Сериализатор возрващаемого значения UpdateView."""

	enough = serializers.BooleanField()


class ResponseResendCodeSerializer(serializers.Serializer):
	"""Сериализатор возрващаемого значения ResendCodeView."""

	result = serializers.CharField(default="Код создан и отправлен")


class ResponseHealthCheckSerializer(serializers.Serializer):
	"""Сериализатор возрващаемого значения HealthCheckView."""

	Health = serializers.CharField(default="OK")
