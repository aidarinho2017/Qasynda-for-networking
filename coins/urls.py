# coins/urls.py
from rest_framework.routers import DefaultRouter
from .views import CoinTransactionViewSet

router = DefaultRouter()
router.register(r'coins', CoinTransactionViewSet, basename='coin-transactions')

urlpatterns = router.urls
