from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=50)
    bio = models.TextField(max_length=144, blank=True)
    profile_picture = CloudinaryField("image", blank=True, null=True)

    def __str__(self):
        name = self.display_name or self.user.username
        return f"{name} Profile"
