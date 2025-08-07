from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomCookieJWTAuthentication(JWTAuthentication):
  def authenticate(self, request):
    # Get access token from cookie
    access_token = request.COOKIES.get("access_token")
    if not access_token:
      return None

    # Use SimpleJWT's authenticate_credentials
    try:
      validated_token = self.get_validated_token(access_token)
      user = self.get_user(validated_token)
    except Exception:
      raise AuthenticationFailed("Invalid or expired token")

    return (user, validated_token)
