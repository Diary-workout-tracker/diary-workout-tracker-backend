from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import (
	AchievementViewSet,
	HealthCheckView,
	MyInfoView,
	RegisterUserView,
	ResendCodeView,
	TokenRefreshView,
	TrainingView,
	HistoryView,
)


router = DefaultRouter()
router.register("achievement", AchievementViewSet, basename="achievement")

urlpatterns = (
	path("health/", HealthCheckView.as_view(), name="health"),
	path("schema/", SpectacularAPIView.as_view(), name="schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
	path("user/", RegisterUserView.as_view(), name="user-register"),
	path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
	path("me/", MyInfoView.as_view(), name="me"),
	path("resend_code/", ResendCodeView.as_view(), name="code-resend"),
	path("training/", TrainingView.as_view(), name="training"),
	path("history/", HistoryView.as_view(), name="history"),
	path("", include(router.urls)),
)
