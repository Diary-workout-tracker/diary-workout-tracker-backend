from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import path
# from rest_framework.routers import DefaultRouter

from .views import HealthCheckView


# router_v1 = DefaultRouter()
# router_v1.register('health', HealthCheckView.as_view(), 'health')

urlpatterns = (
	# path('v1/', include(router_v1.urls)),
	path("v1/health/", HealthCheckView.as_view(), name="health"),
	path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
	path("v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
)
