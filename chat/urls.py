from django.urls import path
from chat.views import RegisterView, ActivateView, ResendActivationView, LogoutView, CustomTokenObtainPairView, UserInfoView
from rest_framework_simplejwt.views import (
  TokenObtainPairView,
  TokenRefreshView,
  TokenBlacklistView,
)

urlpatterns = [
  path('register/', RegisterView.as_view(), name='register'),
  path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
  path('resend-activation/', ResendActivationView.as_view(), name='resend_activation'),
  # path('login/', TokenObtainPairView.as_view(), name='login'),
  path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('logout/', LogoutView.as_view(), name='logout'),
  path("me/", UserInfoView.as_view()),
]
