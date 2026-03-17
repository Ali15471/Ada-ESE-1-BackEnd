from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=80)
    bio = models.TextField(max_length=200, blank=True)
    profile_picture = models.URLField(blank=True)

    def __str__(self):
        return self.display_name or self.user.username