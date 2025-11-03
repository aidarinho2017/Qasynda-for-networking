from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    interests = models.TextField(blank=True, help_text="Comma-separated interests")
    coins = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email or self.user.username

