from django.conf import settings
from django.db import models
from django.utils import timezone
from members.models import Event

class Participation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'event')  # prevent duplicates

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"
