# coins/serializers.py
from rest_framework import serializers
from .models import CoinTransaction

class CoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTransaction
        fields = ['id', 'amount', 'reason', 'created_at']
