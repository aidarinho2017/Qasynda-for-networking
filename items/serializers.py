# items/serializers.py
from rest_framework import serializers
from .models import Item, UserItem, ItemPriceHistory, ItemListing

class ItemPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPriceHistory
        fields = ["price", "changed_at"]


class ItemSerializer(serializers.ModelSerializer):
    price_history = ItemPriceHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "description", "type", "cost", "available_quantity", "status", "image_url", "price_history", "created_at", "updated_at"]


class UserItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), source="item", write_only=True)

    class Meta:
        model = UserItem
        fields = ["id", "item", "item_id", "quantity", "purchase_price", "created_at"]


class ItemListingSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    seller_username = serializers.CharField(source="seller.username", read_only=True)

    class Meta:
        model = ItemListing
        fields = ["id", "item", "seller", "seller_username", "quantity", "price_per_unit", "created_at"]
