from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, validators=[validate_password])

  class Meta:
    model = User
    fields = ['email', 'password']

  def create(self, validated_data):
    user = User.objects.create_user(
      email=validated_data['email'],
      password=validated_data['password']
    )
    return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    data = super().validate(attrs)

    # Include additional user data in the response
    data['user'] = {
      'id': self.user.id,
      'email': self.user.email,
    }

    return data
