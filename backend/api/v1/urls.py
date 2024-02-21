from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import HealthCheckView

from django.urls import path


urlpatterns = (
	path("v1/health/", HealthCheckView.as_view(), name="health"),
	path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
	path("v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
)
