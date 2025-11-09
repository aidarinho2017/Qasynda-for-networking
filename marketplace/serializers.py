from rest_framework import serializers
from .models import Listing
from items.models import Item


class ListingSerializer(serializers.ModelSerializer):
    item_id = serializers.PrimaryKeyRelatedField(source='item', queryset=Item.objects.all(), write_only=True)
    item = serializers.PrimaryKeyRelatedField(read_only=True)
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_type = serializers.CharField(source="item.type", read_only=True)

    class Meta:
        model = Listing
        fields = ["id", "seller", "seller_username", "item", "item_id", "item_name", "item_type", "quantity", "price_per_unit", "created_at", "updated_at"]
        read_only_fields = ["seller", "created_at", "updated_at", "seller_username", "item_name", "item_type", "item"]
