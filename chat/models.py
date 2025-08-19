from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

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


class Conversation(models.Model):
  participants = models.ManyToManyField(User, related_name='conversations')
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Conversation {self.id}"

  def get_other_user(self, current_user):
    return self.participants.exclude(id=current_user.id).first()


class Message(models.Model):
  conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
  sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
  content = models.TextField()
  timestamp = models.DateTimeField(auto_now_add=True)
  is_read = models.BooleanField(default=False)

  def __str__(self):
    return f"From {self.sender.email} at {self.timestamp}"