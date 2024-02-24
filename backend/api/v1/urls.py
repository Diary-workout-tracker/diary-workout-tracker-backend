from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import HealthCheckView, register_user

from django.urls import path


urlpatterns = (
	path("health/", HealthCheckView.as_view(), name="health"),
	path("schema/", SpectacularAPIView.as_view(), name="schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
	path("user/", register_user, name="user-register"),
)
