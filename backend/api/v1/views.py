from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from running.models import Achievement, Day, UserAchievement
from utils import authcode, mailsender, motivation_phrase
from .serializers import (
	AchievementSerializer,
	CustomTokenObtainSerializer,
	TrainingSerializer,
	UserAchievementSerializer,
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
		user = get_object_or_404(User, email=request.data.get("email"))
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
		queryset = self.queryset.all()
		history = user.user_history.all()
		dynamic_motivation_phrase = motivation_phrase.get_dynamic_list_motivation_phrase(user)
		len_history = len(history)
		for i in range(len(queryset)):
			element = queryset[i]
			if len_history > i:
				element.completed = history[i].completed
			element.motivation_phrase = dynamic_motivation_phrase[i]
		return queryset


@extend_schema_view(
	list=extend_schema(
		responses={200: AchievementSerializer(many=True)},
		summary="Список достижений",
		description="Выводит список достижений",
		tags=("Run",),
	),
	retrieve=extend_schema(
		responses={200: AchievementSerializer()},
		summary="Получение достижения по идентификатору",
		description="Получает информацию о достижение по его идентификатору",
		tags=("Run",),
	),
	me=extend_schema(
		responses={200: UserAchievementSerializer()},
		summary="Получение достижений авторизированного пользователя",
		description="Получает информацию о достижениях авторизированного пользователя",
		tags=("Run",),
	),
)
class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Achievement.objects.all()
	serializer_class = AchievementSerializer

	@action(
		detail=False,
		serializer_class=UserAchievementSerializer,
	)
	def me(self, request: WSGIRequest) -> Response:
		user = request.user
		queryset = UserAchievement.objects.filter(user_id=user)
		serializer = self.serializer_class(queryset, many=True)
		return Response(serializer.data)


class HistoryView(generics.ListCreateAPIView):
	serializer_class = HistorySerializer

	def get_queryset(self) -> QuerySet:
		"""Формирует список историй тренировок пользователя."""
		return self.request.user.user_history.all()
