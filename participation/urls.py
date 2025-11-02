# participation/urls.py
from rest_framework.routers import DefaultRouter
from .views import ParticipationViewSet

router = DefaultRouter()
router.register(r'participations', ParticipationViewSet, basename='participation')

urlpatterns = router.urls
