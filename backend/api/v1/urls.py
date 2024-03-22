from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (
	AchievementViewSet,
	HealthCheckView,
	# test
	HistoryView,
	MyInfoView,
	RegisterUserView,
	ResendCodeView,
	TokenRefreshView,
	TrainingView,
)

urlpatterns = (
	path("achievements/", AchievementViewSet.as_view(), name="achievements"),
	path("health/", HealthCheckView.as_view(), name="health"),
	path("schema/", SpectacularAPIView.as_view(), name="schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
	path("user/", RegisterUserView.as_view(), name="user-register"),
	path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
	path("me/", MyInfoView.as_view(), name="me"),
	path("resend_code/", ResendCodeView.as_view(), name="code-resend"),
	path("training/", TrainingView.as_view(), name="training"),
	# path("test/", test, name="test")
	path("history/", HistoryView.as_view(), name="history"),
)
