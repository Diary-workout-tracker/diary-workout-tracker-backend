from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import HealthCheckView

from django.urls import path, include

djoser_urlpatterns = [path("", include("djoser.urls")), path("", include("djoser.urls.jwt"))]

urlpatterns = (
	path("health/", HealthCheckView.as_view(), name="health"),
	path("schema/", SpectacularAPIView.as_view(), name="schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
	path("", include(djoser_urlpatterns)),
)
