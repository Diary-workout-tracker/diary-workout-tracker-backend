from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from .serializers import CustomUserSerializer
from utils import authcode, mailsender

# from djoser.views import UserViewSet
from django.contrib.auth import get_user_model


User = get_user_model()


def send_auth_code(user) -> None:
	auth_code = authcode.AuthCode(user)
	auth_code.set_sender(mailsender.DefaultMailSender())
	auth_code.create_code()


@permission_classes((AllowAny,))
class HealthCheckView(APIView):
	@extend_schema(
		summary="Проверка работы",
		description="Проверка работы АПИ",
		responses={200: {"Health": "OK"}},
		tags=("System",),
	)
	def get(self, request):
		return Response({"Health": "OK"})


# class CustomUserViewSet(ModelViewSet):
# 	queryset = User.objects.all()
# 	serializer_class = CustomUserSerializer


@api_view(["POST"])
@permission_classes((AllowAny,))
def register_user(request):
	serializer = CustomUserSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		send_auth_code(User.objects.get(email=request.data["email"]))
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
