# coins/views.py
from rest_framework import viewsets, permissions
from .models import CoinTransaction
from .serializers import CoinTransactionSerializer

class CoinTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CoinTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CoinTransaction.objects.filter(user=self.request.user).order_by('-created_at')
