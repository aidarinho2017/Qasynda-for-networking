from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter, OrderingFilter

from . import serializers
from .models import Listing
from .serializers import ListingSerializer
from items.models import UserItem


class ListingViewSet(viewsets.ModelViewSet):
    """
    Marketplace listings.
    GET /api/marketplace/listings/ - list all listings
    POST /api/marketplace/listings/ - create listing (from user's inventory)
    GET /api/marketplace/listings/{id}/ - detail
    PUT/PATCH /api/marketplace/listings/{id}/ - update (only seller)
    DELETE /api/marketplace/listings/{id}/ - delete (only seller)
    POST /api/marketplace/listings/{id}/buy/ - buy from listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['item__name', 'seller__username']
    ordering_fields = ['created_at', 'price_per_unit']

    def perform_create(self, serializer):
        # Create listing from user's inventory
        item = serializer.validated_data['item']
        quantity = serializer.validated_data['quantity']
        user_item = get_object_or_404(UserItem, user=self.request.user, item=item)
        if user_item.quantity < quantity:
            raise serializers.ValidationError("Not enough items in inventory")
        user_item.quantity -= quantity
        if user_item.quantity == 0:
            user_item.delete()
        else:
            user_item.save()
        serializer.save(seller=self.request.user)

    def get_queryset(self):
        return Listing.objects.select_related('seller', 'item')

    def perform_update(self, serializer):
        if serializer.instance.seller != self.request.user:
            raise serializers.ValidationError("You can only update your own listings")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.seller != self.request.user:
            raise serializers.ValidationError("You can only delete your own listings")
        from items.models import UserItem
        user_item, created = UserItem.objects.get_or_create(
            user=instance.seller,
            item=instance.item,
            defaults={'quantity': 0}
        )
        user_item.quantity += instance.quantity
        user_item.save()
        instance.delete()

    @action(detail=True, methods=["post"], url_path="buy")
    def buy(self, request, pk=None):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.seller == request.user:
            return Response({"success": False, "message": "Cannot buy your own listing"}, status=status.HTTP_400_BAD_REQUEST)
        qty = int(request.data.get("quantity", 1))
        result = listing.buy_from_listing(request.user, quantity=qty)
        if result.get("success"):
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # Prevent changing the item in update
        request.data.pop('item_id', None)
        instance = self.get_object()
        old_quantity = instance.quantity
        # Manually update the fields
        if 'quantity' in request.data:
            new_quantity = request.data['quantity']
            if new_quantity > old_quantity:
                # Need more items from inventory
                additional = new_quantity - old_quantity
                user_item = get_object_or_404(UserItem, user=instance.seller, item=instance.item)
                if user_item.quantity < additional:
                    raise serializers.ValidationError("Not enough items in inventory to increase listing quantity")
                user_item.quantity -= additional
                if user_item.quantity == 0:
                    user_item.delete()
                else:
                    user_item.save()
            elif new_quantity < old_quantity:
                # Return excess to inventory
                excess = old_quantity - new_quantity
                from items.models import UserItem
                user_item, created = UserItem.objects.get_or_create(
                    user=instance.seller,
                    item=instance.item,
                    defaults={'quantity': 0}
                )
                user_item.quantity += excess
                user_item.save()
            instance.quantity = new_quantity
        if 'price_per_unit' in request.data:
            instance.price_per_unit = request.data['price_per_unit']
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
