import os
from django.utils import timezone

import requests
from django.conf import settings
from django.db import models

YANDEX_API_KEY = os.getenv("YANDEX_MAP_API")

class Event(models.Model):
    title = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    latitude = models.FloatField(default=43.238946)
    longitude = models.FloatField(default=76.889709)

    organizer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='organized_events')
    chat_link = models.CharField(max_length=255, blank=True, help_text="Telegram, WhatsApp, or phone")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-geocode address if missing coordinates
        if self.address and (not self.latitude or not self.longitude):
            try:
                url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&format=json&geocode={self.address}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                point_str = (
                    data["response"]["GeoObjectCollection"]["featureMember"][0]
                    ["GeoObject"]["Point"]["pos"]
                )
                lon, lat = map(float, point_str.split())
                self.latitude = lat
                self.longitude = lon
            except Exception as e:
                print(f"Geocoding failed: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.date})"


class Interests(models.Model):
    interests = models.CharField(max_length=500)

class Recommendation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    interest = models.CharField(max_length=100)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
