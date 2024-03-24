from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Case, DateTimeField, F, Q, URLField, When
from django.db.models.query import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from running.models import Achievement, Day
from utils import authcode, mailsender, motivation_phrase, users
from .serializers import (
	AchievementSerializer,
	AchievementEndTrainingSerializer,
	CustomTokenObtainSerializer,
	TrainingSerializer,
	UserSerializer,
	HistorySerializer,
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
class AchievementViewSet(generics.ListAPIView):
	serializer_class = AchievementSerializer

	def get_queryset(self) -> QuerySet:
		"""Формирует список ачивок c флагом получения и датой."""
		user = self.request.user
		queryset = (
			Achievement.objects.annotate(
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

	def get_queryset(self) -> QuerySet:
		"""Формирует список историй тренировок пользователя."""
		return self.request.user.user_history.all().order_by("training_day")

	def create(self, request: Request, *args, **kwargs) -> Response:
		achievements = request.data.pop("achievements", None)  # noqa
		HistorySerializer.validate_achievements(self, achievements)
		# XXX Тут можно начать просчёт ачивок.

		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)

		new_achievements = AchievementEndTrainingSerializer(
			Achievement.objects.all(), many=True, context={"request": request}
		).data  # XXX Тут в будущем вместо всех ачивок надо добавить новые.

		return Response(new_achievements, status=status.HTTP_201_CREATED, headers=headers)


# from rest_framework.decorators import api_view
# from utils.achievements import AchievementUpdater
# @api_view(("POST", ))
# def test(request):
# 	user = request.user
# 	updater = AchievementUpdater(user, request.data)
# 	updater.update_achievements()
# 	return Response('')
