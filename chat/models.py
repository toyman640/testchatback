from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
        raise ValueError("Email is required")
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save()
    return user

  def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
  email = models.EmailField(unique=True)
  is_active = models.BooleanField(default=False)  # User must activate via email
  is_staff = models.BooleanField(default=False)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  objects = UserManager()

  def __str__(self):
    return self.email
