from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Extend later if needed (profile picture, preferences, etc.)
    pass
