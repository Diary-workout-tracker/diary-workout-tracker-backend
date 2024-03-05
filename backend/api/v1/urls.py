from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import (
	AchievementListView,
	HealthCheckView,
	MyInfoView,
	RegisterUserView,
	ResendCodeView,
	TokenRefreshView,
)

router = DefaultRouter()
router.register("achivment", AchievementListView, basename="achivment")

urlpatterns = (
	path("health/", HealthCheckView.as_view(), name="health"),
	path("schema/", SpectacularAPIView.as_view(), name="schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
	path("user/", RegisterUserView.as_view(), name="user-register"),
	path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
	path("me/", MyInfoView.as_view(), name="me"),
	path("resend_code/", ResendCodeView.as_view(), name="code-resend"),
	path("", include(router.urls)),
)
