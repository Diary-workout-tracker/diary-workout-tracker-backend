from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response


class HealthCheckView(APIView):
	@extend_schema(
		summary="Проверка работы",
		description="Проверка работы АПИ",
		responses={200: {"Health": "OK"}},
		tags=("System",),
	)
	def get(self, request):
		return Response({"Health": "OK"})
