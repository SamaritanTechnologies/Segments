from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _
from accounts.managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
