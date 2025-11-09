from django.conf import settings
from django.db import models
from django.utils import timezone

class CoinTransaction(models.Model):
    REASON_CHOICES = [
        ('EVENT_CREATE', 'Event creation'),
        ('PARTICIPATE', 'Participation'),
        ('CANCEL', 'Cancel participation'),
        ('REGISTRATION', 'User registration'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_transactions")
    amount = models.IntegerField()
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}: {self.amount} ({self.reason})"
