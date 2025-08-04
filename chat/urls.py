from django.urls import path
from accounts.views import RegisterView, ActivateView
from rest_framework_simplejwt.views import (
  TokenObtainPairView,
  TokenRefreshView,
  TokenBlacklistView,
)

urlpatterns = [
  path('register/', RegisterView.as_view(), name='register'),
  path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
  path('login/', TokenObtainPairView.as_view(), name='login'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('logout/', TokenBlacklistView.as_view(), name='logout'),
]
