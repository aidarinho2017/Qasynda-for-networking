from django.db import models

class Event(models.Model):
  title = models.CharField(max_length=50)
  address = models.CharField(max_length=255)
  category = models.CharField(max_length=100)

class Interests(models.Model):
    interests = models.CharField(max_length=500)

class Recommendation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    interest = models.CharField(max_length=100)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
