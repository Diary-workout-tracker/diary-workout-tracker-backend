import base64
from collections import OrderedDict
import datetime

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from running.models import Achievement, Day, History, MotivationalPhrase
from .constants import FORMAT_DATE
from .validators import CustomUniqueValidator
from users.models import GENDER_CHOICES
from running.models import Day
from utils.authcode import AuthCode
from utils.users import get_user_by_email_or_404


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
		if value:
			return self.context["request"].build_absolute_uri(value.url)
		return


class UserSerializer(serializers.ModelSerializer):
	"""Сериализатор кастомного пользователя."""

	email = serializers.EmailField(validators=(CustomUniqueValidator(queryset=User.objects.all()),))
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
	achievements = serializers.ListField(required=False, write_only=True, child=serializers.CharField())

	class Meta:
		model = History
		fields = (
			"training_start",
			"training_end",
			"completed",
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
			"training_start": {"write_only": True},
			"completed": {"write_only": True},
			"training_day": {"write_only": True},
			"cities": {"write_only": True},
			"max_speed": {"write_only": True, "min_value": 0},
			"distance": {"min_value": 0},
			"avg_speed": {"min_value": 0},
			"route": {"required": False},
		}

	def validate(self, data: OrderedDict) -> OrderedDict:
		if data["training_start"] >= data["training_end"]:
			raise serializers.ValidationError(
				{"training_start_training_end": ["Время начала тренировки должно быть раньше конца"]}
			)
		return data

	def validate_motivation_phrase(self, value: str) -> str:
		if not MotivationalPhrase.objects.filter(text=value).count():
			raise serializers.ValidationError("Данной мотивационной фразы не существует")
		return value

	def validate_achievements(self, value: list) -> list:
		if value and len(value) > Achievement.objects.filter(title__in=value).count():
			raise serializers.ValidationError({"achievements": ["Некорректные ачивки"]})
		return value

	def get_time(self, obj: History) -> int:
		"""Отдаёт продолжительность тренировки."""
		return (obj.training_end - obj.training_start).total_seconds() // 60

	def create(self, validated_data: dict) -> History:
		validated_data["user_id"] = self.context["request"].user
		return super().create(validated_data)
