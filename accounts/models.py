from django.contrib.auth.models import AbstractUser
from django.db import models
from zoneinfo import available_timezones

class User(AbstractUser):
    email = models.EmailField(unique=True)

    timezone = models.CharField(
    max_length=50,
    choices=[(tz, tz) for tz in sorted(available_timezones())],
    default="UTC"
    )
    
    REQUIRED_FIELDS = ['email']
