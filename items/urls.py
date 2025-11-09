# items/urls.py
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, UserItemViewSet, ItemListingViewSet, MyListingsViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="items")
router.register(r"my-items", UserItemViewSet, basename="my-items")
router.register(r"listings", ItemListingViewSet, basename="listings")
router.register(r"my-listings", MyListingsViewSet, basename="my-listings")

urlpatterns = [
    path("", include(router.urls)),
]
