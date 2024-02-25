from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import HealthCheckView, RegisterUserView, TokenRefreshView, MyInfoView
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register('me', MyInfoViewSet, basename='me')

urlpatterns = (
	path("health/", HealthCheckView.as_view(), name="health"),
	path("schema/", SpectacularAPIView.as_view(), name="schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
	path("user/", RegisterUserView.as_view(), name="user-register"),
	path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
	path("me/", MyInfoView.as_view(), name="me"),
	# path("", include(router.urls))
	# path("test/", test_view, name='test')
)
