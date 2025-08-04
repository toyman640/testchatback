from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer
from .utils import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

class RegisterView(APIView):
  def post(self, request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
      user = serializer.save()
      uid = urlsafe_base64_encode(force_bytes(user.pk))
      token = account_activation_token.make_token(user)

      activation_link = f"http://localhost:3000/activate/{uid}/{token}/"

      send_mail(
        "Activate your account",
        f"Click the link to activate: {activation_link}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
      )

      return Response({"message": "Activation email sent."}, status=status.HTTP_201_CREATED)
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
