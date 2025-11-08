# items/urls.py
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, UserItemViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="items")
router.register(r"my-items", UserItemViewSet, basename="my-items")

urlpatterns = [
    path("", include(router.urls)),
]
