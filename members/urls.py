# members/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.events import EventViewSet
from .views.recommend import recommend_events

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('events/recommend/', recommend_events, name='recommend-events'),
]

urlpatterns += router.urls
