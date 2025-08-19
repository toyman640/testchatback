from django.shortcuts import render
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer
from .utils import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.utils.timezone import now
from datetime import timedelta


# class RegisterView(APIView):
#   def post(self, request):
#     serializer = RegisterSerializer(data=request.data)
#     if serializer.is_valid():
#       user = serializer.save()
#       uid = urlsafe_base64_encode(force_bytes(user.pk))
#       token = account_activation_token.make_token(user)

#       frontend_base_url = "http://localhost:5173"
#       activation_link = f"{frontend_base_url}/account-activated/{uid}/{token}/"

#       # domain = request.get_host()  # dynamically get current host
#       # scheme = "https" if request.is_secure() else "http"
#       # activation_link = f"{scheme}://{domain}/activate/{uid}/{token}/"

#       send_mail(
#         "Activate your account",
#         f"Click the link to activate: {activation_link}",
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#         fail_silently=False,
#       )

#       return Response({"message": "Activation email sent."}, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
  def post(self, request):
    email = request.data.get("email")

    # ✅ Check if a user with that email exists
    existing_user = User.objects.filter(email=email).first()
    if existing_user:
      if not existing_user.is_active:
        return Response(
          {"error": "Email is registered but not activated. Please check your email for activation link."},
          status=status.HTTP_400_BAD_REQUEST
        )
      else:
        return Response(
          {"Note": "Email is already registered and active. Please log in instead."},
          status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Continue with normal registration if no existing user
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
      user = serializer.save()

      # Generate activation link
      uid = urlsafe_base64_encode(force_bytes(user.pk))
      token = account_activation_token.make_token(user)

      frontend_base_url = "http://localhost:5173"
      activation_link = f"{frontend_base_url}/account-activated/{uid}/{token}/"

      # Send email
      send_mail(
        "Activate your account",
        f"Click the link to activate: {activation_link}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
      )

      return Response(
        {"message": "Activation email sent."},
        status=status.HTTP_201_CREATED
      )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateView(APIView):
  def get(self, request, uidb64, token):
    try:
      uid = force_str(urlsafe_base64_decode(uidb64))
      user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
      return Response({'error': 'Invalid link'}, status=400)

    if account_activation_token.check_token(user, token):
      user.is_active = True
      user.save()
      return Response({'message': 'Account activated'}, status=200)
    else:
      return Response({'error': 'Invalid or expired token'}, status=400)



class ResendActivationView(APIView):
  permission_classes = [AllowAny]

  def post(self, request):
    email = request.data.get("email")
    try:
      user = User.objects.get(email=email)
      if user.is_active:
        return Response({"message": "Account is already active."}, status=status.HTTP_400_BAD_REQUEST)

      uid = urlsafe_base64_encode(force_bytes(user.pk))
      token = account_activation_token.make_token(user)

      # domain = request.get_host()
      # scheme = "https" if request.is_secure() else "http"
      # activation_link = f"{scheme}://{domain}/activate/{uid}/{token}/"
      frontend_base_url = "http://localhost:5173"
      activation_link = f"{frontend_base_url}/account-activated/{uid}/{token}/"

      send_mail(
        "Resend Activation Link",
        f"Click the link to activate your account: {activation_link}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
      )
      return Response({"message": "Activation email resent."}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
      return Response({"error": "No account found with this email."}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)

            # Clear cookies
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class LogoutView(APIView):
#   permission_classes = [AllowAny]  # allow logout even if token is expired

#   def post(self, request):
#     refresh_token = request.data.get("refresh")

#     if not refresh_token:
#       return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#       token = RefreshToken(refresh_token)
#       token.blacklist()
#       return Response({"message": "Token blacklisted successfully."}, status=status.HTTP_205_RESET_CONTENT)

#     except TokenError as e:
#       return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


# class CustomTokenObtainPairView(TokenObtainPairView):
#   serializer_class = CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
  serializer_class = CustomTokenObtainPairSerializer

  def post(self, request, *args, **kwargs):
    response = super().post(request, *args, **kwargs)
    data = response.data

    # Extract tokens
    access = data.get("access")
    refresh = data.get("refresh")

    if access and refresh:
      # Set cookies
      access_token_expiry = now() + timedelta(minutes=5)  # match JWT lifespan
      refresh_token_expiry = now() + timedelta(days=1)

      response.set_cookie(
        "access_token",
        access,
        expires=access_token_expiry,
        httponly=True,
        secure=False,  # ✅ Set to True in production
        samesite="Lax"
      )

      response.set_cookie(
        "refresh_token",
        refresh,
        expires=refresh_token_expiry,
        httponly=True,
        secure=False,  # ✅ Set to True in production
        samesite="Lax"
      )

      return response


class UserInfoView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    user = request.user
    return Response({
      "id": user.id,
      "email": user.email,
    })
