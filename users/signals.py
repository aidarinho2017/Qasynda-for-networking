from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from coins.models import CoinTransaction

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        # кол-во монет за регистрацию
        profile.coins += 10
        profile.save()
        CoinTransaction.objects.create(user=instance, amount=10, reason="REGISTRATION")  # or new reason
