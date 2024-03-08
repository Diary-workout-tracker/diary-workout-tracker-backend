from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from utils import authcode, mailsender, motivation_phrase

from .serializers import CustomTokenObtainSerializer, UserSerializer, TrainingSerializer
from .throttling import CodeRequestThrottle
from running.models import Day

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
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid():
			serializer.save()
			send_auth_code(User.objects.get(email=request.data["email"]))
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendCodeView(APIView):
	permission_classes = (AllowAny,)
	throttle_classes = (CodeRequestThrottle,)

	def post(self, request):
		user = get_object_or_404(User, email=request.data.get("email"))
		send_auth_code(user)
		return Response({"result": "Код создан и отправлен"}, status=status.HTTP_201_CREATED)


class TokenRefreshView(APIView):
	serializer_class = CustomTokenObtainSerializer
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
		serializer = self.serializer_class(user)
		return Response(serializer.data)

	def patch(self, request, *args, **kwargs):
		user = request.user
		serializer = self.serializer_class(user, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, *args, **kwargs):
		user = request.user
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class TrainingView(ListAPIView):
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
