# members/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.events import EventViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')

urlpatterns = []

urlpatterns += router.urls
