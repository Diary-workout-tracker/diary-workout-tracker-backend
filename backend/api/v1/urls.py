from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

<<<<<<< HEAD
from .views import HealthCheckView, MyInfoView, RegisterUserView, TokenRefreshView

router = DefaultRouter()

=======
>>>>>>> 93bca32 (poetry, pyproject.toml, djoser, simplejwt conflicts)
urlpatterns = (
	path("health/", HealthCheckView.as_view(), name="health"),
	path("schema/", SpectacularAPIView.as_view(), name="schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
<<<<<<< HEAD
	path("user/", RegisterUserView.as_view(), name="user-register"),
	path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
	path("me/", MyInfoView.as_view(), name="me"),
=======
>>>>>>> 93bca32 (poetry, pyproject.toml, djoser, simplejwt conflicts)
)
