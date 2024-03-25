from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Case, DateTimeField, F, Q, URLField, When
from django.db.models.query import QuerySet
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from running.models import Achievement, Day, History
from users.constants import DEFAULT_AMOUNT_OF_SKIPS
from users.models import User as ClassUser
from utils import authcode, mailsender, motivation_phrase, users

from .serializers import (
	AchievementEndTrainingSerializer,
	AchievementSerializer,
	CustomTokenObtainSerializer,
	HistorySerializer,
	TrainingSerializer,
	UserSerializer,
)
from .throttling import DurationCooldownRequestThrottle

User = get_user_model()


def send_auth_code(user) -> None:
	auth_code = authcode.AuthCode(user)
	auth_code.set_sender(mailsender.DefaultMailSender())
	auth_code.create_code()


class HealthCheckView(APIView):
	permission_classes = (AllowAny,)

	@extend_schema(
		summary="Проверка работы",
		description="Проверка работы АПИ",
		responses={200: {"Health": "OK"}},
		tags=("System",),
	)
	def get(self, request):
		return Response({"Health": "OK"})


class RegisterUserView(APIView):
	serializer_class = UserSerializer
	permission_classes = (AllowAny,)

	def post(self, request, format=None):
		serializer = self.serializer_class(data=request.data, context={"request": request})
		if serializer.is_valid():
			serializer.save()
			send_auth_code(User.objects.get(email=request.data["email"]))
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendCodeView(APIView):
	permission_classes = (AllowAny,)
	throttle_classes = (DurationCooldownRequestThrottle,)

	def post(self, request):
		user = users.get_user_by_email_or_404(request.data.get("email"))
		send_auth_code(user)
		return Response({"result": "Код создан и отправлен"}, status=status.HTTP_201_CREATED)


class TokenRefreshView(APIView):
	serializer_class = CustomTokenObtainSerializer
	throttle_classes = (DurationCooldownRequestThrottle,)
	permission_classes = (AllowAny,)

	def post(self, request, format=None):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid():
			token_data = serializer.save()
			return Response(token_data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyInfoView(APIView):
	serializer_class = UserSerializer

	def get(self, request, *args, **kwargs):
		user = request.user
		serializer = self.serializer_class(user, context={"request": request})
		return Response(serializer.data)

	def patch(self, request, *args, **kwargs):
		user = request.user
		serializer = self.serializer_class(user, data=request.data, context={"request": request}, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, *args, **kwargs):
		user = request.user
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
	get=extend_schema(
		responses={200: TrainingSerializer(many=True)},
		summary="Список тренировок",
		description="Выводит список тренировок",
		tags=("Run",),
	),
)
class TrainingView(generics.ListAPIView):
	queryset = Day.objects.all()
	serializer_class = TrainingSerializer

	def get_queryset(self) -> QuerySet:
		"""
		Формирует список тренировок с динамическими фразами
		и флагом завершения тренировки.
		"""
		user = self.request.user
		queryset = (
			self.queryset.annotate(
				completed=Case(
					When(
						Q(historis__training_day=F("day_number")) & Q(historis__user_id=user),
						then=F("historis__completed"),
					),
					default=False,
					output_field=BooleanField(),
				)
			)
			.all()
			.order_by("day_number")
		)
		dynamic_motivation_phrase = motivation_phrase.get_dynamic_list_motivation_phrase(user)
		for i in range(len(queryset)):
			queryset[i].motivation_phrase = dynamic_motivation_phrase[i]
		return queryset


@extend_schema_view(
	get=extend_schema(
		responses={200: AchievementSerializer(many=True)},
		summary="Список достижений",
		description="Выводит список достижений",
		tags=("Run",),
	),
)
class AchievementView(generics.ListAPIView):
	serializer_class = AchievementSerializer

	def get_queryset(self) -> QuerySet:
		"""Формирует список ачивок c флагом получения и датой."""
		user = self.request.user
		return Achievement.objects.annotate(
			achievement_icon=Case(
				When(user_achievements__user_id=user, then=F("icon")),
				default=F("black_white_icon"),
				output_field=URLField(),
			),
			received=Case(
				When(user_achievements__user_id=user, then=True),
				default=False,
				output_field=BooleanField(),
			),
			achievement_date=Case(
				When(user_achievements__user_id=user, then=F("user_achievements__achievement_date")),
				default=None,
				output_field=DateTimeField(),
			),
		).all()


@extend_schema_view(
	get=extend_schema(
		responses={200: HistorySerializer(many=True)},
		summary="История тренировок",
		description="Выводит историю тренировок",
		tags=("Run",),
	),
	post=extend_schema(
		responses={201: AchievementEndTrainingSerializer(many=True)},
		summary="Сохранение выполненной тренировки",
		description="Сохраняет выполненную тренировку",
		tags=("Run",),
	),
)
class HistoryView(generics.ListCreateAPIView):
	serializer_class = HistorySerializer

	def get_queryset(self) -> QuerySet:
		"""Формирует список историй тренировок пользователя."""
		return self.request.user.user_history.all().order_by("training_day")

	def perform_create(self, serializer: HistorySerializer) -> History:
		"""Создаёт новую историю."""
		return serializer.save()

	def create(self, request: Request, *args, **kwargs) -> Response:
		achievements = request.data.pop("achievements", None)  # noqa
		HistorySerializer.validate_achievements(self, achievements)
		# XXX Тут можно начать просчёт ачивок.

		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		history = self.perform_create(serializer)
		self.request.user.last_completed_training = history
		self.request.user.save()
		headers = self.get_success_headers(serializer.data)

		new_achievements = AchievementEndTrainingSerializer(
			Achievement.objects.all(), many=True, context={"request": request}
		).data  # XXX Тут в будущем вместо всех ачивок надо добавить новые.

		return Response(new_achievements, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema_view(
	get=extend_schema(
		responses={200: {"updated": True}},
		summary="Обновляет заморозки у пользователя",
		description="Обновляет заморозки у пользователя",
		tags=("Run",),
	),
)
class SkipView(APIView):
	def _get_date_activity(self, user: ClassUser) -> datetime:
		"""Отдаёт дату последней активности в виде тренировки или заморозки."""
		date_last_skips = user.date_last_skips
		date_activity = user.last_completed_training.training_start
		if date_last_skips:
			date_activity = date_activity if date_activity > date_last_skips else date_last_skips
		return date_activity

	def _updates_skip_data(
		self, user: ClassUser, amount_of_skips: int, days_missed: int, date_day_ago: datetime
	) -> None:
		"""Обновляет данные по заморозкам пользователя."""
		user.amount_of_skips = amount_of_skips - days_missed
		user.date_last_skips = date_day_ago
		user.save()

	def _clearing_user_training_data(self, user: ClassUser) -> None:
		"""Очищает данные по тренировка пользователя."""
		user.amount_of_skips = DEFAULT_AMOUNT_OF_SKIPS
		user.date_last_skips = None
		user.save()
		History.objects.filter(user_id=user).delete()

	def get(self, request: Request, *args, **kwargs) -> Response:
		user = request.user
		response = Response({"updated": True})
		if not user.last_completed_training:
			return response

		date_activity = self._get_date_activity(user)
		amount_of_skips = user.amount_of_skips
		date_day_ago = timezone.localtime() - timedelta(days=1)
		days_missed = (date_day_ago.date() - date_activity.date()).days
		if days_missed <= 0:
			return response

		if amount_of_skips >= days_missed:
			self._updates_skip_data(user, amount_of_skips, days_missed, date_day_ago)
		else:
			self._clearing_user_training_data(user)
		return response
