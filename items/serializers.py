# items/serializers.py
from rest_framework import serializers
from .models import Item, UserItem

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "description", "type", "cost", "available_quantity", "image_url", "created_at", "updated_at"]


class UserItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), source="item", write_only=True)

    class Meta:
        model = UserItem
        fields = ["id", "item", "item_id", "quantity", "purchase_price", "created_at"]
