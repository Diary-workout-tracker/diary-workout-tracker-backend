from datetime import datetime

import pytz
from django.contrib.auth import get_user_model
from django.db.models import Case, DateTimeField, Exists, F, OuterRef, When
from django.db.models.query import QuerySet
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from running.models import Achievement, Day, History, UserAchievement
from users.constants import DEFAULT_AMOUNT_OF_SKIPS
from users.models import User as ClassUser
from utils import authcode, mailsender, motivation_phrase, users
from utils.achievements import AchievementUpdater
from utils.amount_skips import counts_missed_days

from .serializers import (
	AchievementEndTrainingSerializer,
	AchievementSerializer,
	CustomTokenObtainSerializer,
	HistorySerializer,
	MeSerializer,
	ResponseHealthCheckSerializer,
	ResponseResendCodeSerializer,
	ResponseUpdateSerializer,
	ResponseUserDefaultSerializer,
	TrainingSerializer,
	UserSerializer,
	UserTimezoneSerializer,
)
from .throttling import DurationCooldownRequestThrottle

User = get_user_model()


def send_auth_code(user: ClassUser) -> None:
	auth_code = authcode.AuthCode(user)
	auth_code.set_sender(mailsender.DefaultMailSender())
	auth_code.create_code()


class HealthCheckView(APIView):
	permission_classes = (AllowAny,)

	@extend_schema(
		responses={200: ResponseHealthCheckSerializer()},
		summary="Проверка работы",
		description="Проверка работы API",
		tags=("System",),
	)
	def get(self, request: Request) -> Response:
		return Response({"Health": "OK"})


@extend_schema_view(
	post=extend_schema(
		responses={201: UserSerializer()},
		summary="Создание пользователя",
		description="Создание пользователя",
		tags=("User",),
	),
)
class RegisterUserView(APIView):
	serializer_class = UserSerializer
	permission_classes = (AllowAny,)

	def post(self, request: Request) -> Response:
		serializer = self.serializer_class(data=request.data, context={"request": request})
		if serializer.is_valid():
			serializer.save()
			send_auth_code(User.objects.get(email=request.data["email"]))
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
	post=extend_schema(
		responses={201: ResponseResendCodeSerializer()},
		summary="Повторная отправка кода",
		description="Повторная отправка кода",
		tags=("User",),
	),
)
class ResendCodeView(APIView):
	permission_classes = (AllowAny,)
	throttle_classes = (DurationCooldownRequestThrottle,)
	serializer_class = UserSerializer

	def post(self, request: Request) -> Response:
		user = users.get_user_by_email_or_404(request.data.get("email"))
		send_auth_code(user)
		return Response({"result": "Код создан и отправлен"}, status=status.HTTP_201_CREATED)


@extend_schema_view(
	post=extend_schema(
		responses={200: TokenRefreshSerializer()},
		summary="Обновление токена",
		description="Обновление токена",
		tags=("User",),
	),
)
class TokenRefreshView(APIView):
	serializer_class = CustomTokenObtainSerializer
	throttle_classes = (DurationCooldownRequestThrottle,)
	permission_classes = (AllowAny,)

	def post(self, request: Request) -> Response:
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid():
			token_data: dict = serializer.save()
			token_data.pop("refresh")
			return Response(token_data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
	get=extend_schema(
		responses={200: MeSerializer()},
		summary="Отдаёт данные по пользователю",
		description="Отдаёт данные по пользователю",
		tags=("User",),
	),
	patch=extend_schema(
		responses={200: MeSerializer()},
		summary="Обновляет данные пользователя",
		description="Обновляет данные пользователя",
		tags=("User",),
	),
	put=extend_schema(exclude=True),
	delete=extend_schema(
		responses={204: MeSerializer()},
		summary="Удаляет пользователя",
		description="Удаляет пользователя",
		tags=("User",),
	),
)
class MyInfoView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = MeSerializer

	def get_object(self) -> ClassUser:
		"""Отдаёт объект пользователя."""
		return self.request.user


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

	def get_queryset(self) -> QuerySet[History]:
		"""
		Формирует список тренировок с динамическими фразами
		и флагом завершения тренировки.
		"""
		user = self.request.user
		sub_queryset = History.objects.filter(user_id=user).values("training_day")
		queryset = (
			self.queryset.annotate(completed=Exists(sub_queryset.filter(training_day=OuterRef("day_number"))))
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

	def get_queryset(self) -> QuerySet[Achievement]:
		"""Формирует список ачивок c флагом получения и датой."""
		user = self.request.user
		sub_queryset = UserAchievement.objects.filter(user_id=user).values("achievement_id", "achievement_date")
		queryset = (
			Achievement.objects.annotate(
				received=Exists(sub_queryset.filter(achievement_id=OuterRef("id"))),
				achievement_date=Case(
					When(user_achievements__user_id=user, then=F("user_achievements__achievement_date")),
					default=None,
					output_field=DateTimeField(),
				),
			)
			.all()
			.order_by("id")
			.distinct("id")
		)
		return queryset


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

	def get_queryset(self) -> QuerySet[History]:
		"""Формирует список историй тренировок пользователя."""
		return self.request.user.user_history.order_by("training_day")

	def perform_create(self, serializer: HistorySerializer) -> History:
		"""Создаёт новую историю."""
		return serializer.save()

	def _update_data_user(self, user: ClassUser, history: History) -> None:
		user.last_completed_training = history
		user.total_m_run += history.distance
		user.save()

	def create(self, request: Request, *args, **kwargs) -> Response:
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		if "achievements" in serializer._validated_data.keys():
			serializer._validated_data.pop("achievements")
		history = self.perform_create(serializer)
		user = self.request.user
		achievements = request.data.get("achievements")
		self._update_data_user(user, history)
		updater = AchievementUpdater(user, achievements, history)
		updater.update_achievements()
		headers = self.get_success_headers(serializer.data)

		new_achievements = AchievementEndTrainingSerializer(
			updater.new_achievements, many=True, context={"request": request}
		).data
		return Response(new_achievements, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema_view(
	patch=extend_schema(
		responses={200: ResponseUpdateSerializer()},
		summary="Обновляет заморозки у пользователя и сохраняет часовой пояс",
		description="Обновляет заморозки у пользователя и сохраняет часовой пояс",
		tags=("User",),
	),
)
class UpdateView(APIView):
	serializer_class = UserTimezoneSerializer

	def _updates_skip_data(
		self, user: ClassUser, amount_of_skips: int, days_missed: int, date_day_ago: datetime
	) -> None:
		"""Обновляет данные по заморозкам пользователя."""
		user.amount_of_skips = amount_of_skips - days_missed
		user.date_last_skips = date_day_ago
		user.save()

	def _set_null_amount_of_skip(self, user: ClassUser) -> None:
		"""
		Устанавливает значение заморозок у пользователя равное нулю
		и блокирует тренировки.
		"""
		user.amount_of_skips = 0
		user.blocked_training = True
		user.save()

	def _update_user_timezone_data(self, user: ClassUser, user_timezone: str) -> None:
		"""Обновляет timezone ползователя."""
		if user.timezone != user_timezone:
			user.timezone = user_timezone
			user.save()

	def patch(self, request: Request, *args, **kwargs) -> Response:
		"""Обновляет timezone пользователя и просчитывает пропуски тренировок."""
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		user_timezone = request.data.get("timezone")
		response_data = {
			"data": {
				"enough": True,
				"skip": False,
			},
			"status": status.HTTP_200_OK,
		}
		user: ClassUser = request.user
		last_traning: History = user.last_completed_training
		if user.blocked_training:
			response_data["data"]["enough"] = False
			self._update_user_timezone_data(user, user_timezone)
			return Response(**response_data)
		if not last_traning or last_traning.training_day.day_number == 100:
			self._update_user_timezone_data(user, user_timezone)
			return Response(**response_data)
		now = timezone.localtime(timezone=pytz.timezone(user_timezone))
		days_missed, date_day_ago, amount_of_skips = counts_missed_days(user, user_timezone, now)
		if days_missed <= 0:
			self._update_user_timezone_data(user, user_timezone)
			return Response(**response_data)
		user.timezone = user_timezone
		if amount_of_skips >= days_missed:
			self._updates_skip_data(user, amount_of_skips, days_missed, date_day_ago)
			response_data["data"]["skip"] = True
			return Response(**response_data)
		self._set_null_amount_of_skip(user)
		response_data["data"]["enough"] = False
		response_data["data"]["skip"] = True
		return Response(**response_data)


@extend_schema_view(
	patch=extend_schema(
		responses={200: ResponseUserDefaultSerializer()},
		summary="Очищает данные по тренировкам и ачивки пользователя",
		description="Очищает данные по тренировкам и ачивки пользователя",
		tags=("User",),
	),
)
class UserDefaultView(APIView):
	def patch(self, request: Request, *args, **kwargs) -> Response:
		"""Очищает данные по тренировкам и ачивки пользователя."""
		user: ClassUser = request.user
		user.date_last_skips = None
		user.amount_of_skips = DEFAULT_AMOUNT_OF_SKIPS
		user.total_m_run = 0
		user.blocked_training = False
		user.save()
		user_history: QuerySet[History] = user.user_history.all()
		user_history.delete()
		user_achievements: QuerySet[UserAchievement] = user.user_achievements.all()
		user_achievements.delete()
		return Response({"default": True}, status=status.HTTP_200_OK)
