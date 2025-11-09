# items/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Item, UserItem, ItemListing
from .serializers import ItemSerializer, UserItemSerializer, ItemListingSerializer


class ItemViewSet(viewsets.ModelViewSet):
    """
    /api/items/           GET list, POST create (admin)
    /api/items/{pk}/      GET retrieve, PUT/PATCH/DELETE (admin)
    Actions:
      POST /api/items/{pk}/buy/   -> buy item
      POST /api/items/{pk}/sell/  -> sell back to system
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes_by_action = {
        "create": [IsAuthenticated],  # you may restrict to admin in practice
        "update": [IsAuthenticated],
        "partial_update": [IsAuthenticated],
        "destroy": [IsAuthenticated],
        "buy": [IsAuthenticated],
        "sell": [IsAuthenticated],
    }

    def get_permissions(self):
        if hasattr(self, "action") and self.action in self.permission_classes_by_action:
            return [perm() for perm in self.permission_classes_by_action[self.action]]
        return [AllowAny()]

    @action(detail=True, methods=["post"], url_path="buy")
    def buy(self, request, pk=None):
        item = get_object_or_404(Item, pk=pk)
        if getattr(item, 'status', 'in_sell') == 'soon':
            return Response({"success": False, "message": "Item is not available for purchase yet"}, status=status.HTTP_400_BAD_REQUEST)
        qty = int(request.data.get("quantity", 1))
        result = item.buy(request.user, quantity=qty)
        if result.get("success"):
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="sell")
    def sell(self, request, pk=None):
        item = get_object_or_404(Item, pk=pk)
        qty = int(request.data.get("quantity", 1))
        sell_price = request.data.get("sell_price", None)
        if sell_price is not None:
            try:
                sell_price = int(sell_price)
            except ValueError:
                return Response({"success": False, "message": "Invalid sell_price"}, status=status.HTTP_400_BAD_REQUEST)
        result = item.sell_back(request.user, quantity=qty, sell_price=sell_price)
        if result.get("success"):
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class UserItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/my-items/  -> list user's items
    """
    serializer_class = UserItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserItem.objects.filter(user=self.request.user).select_related("item")

    @action(detail=True, methods=["post"], url_path="list")
    def list_for_sale(self, request, pk=None):
        user_item = get_object_or_404(UserItem, pk=pk, user=request.user)
        qty = int(request.data.get("quantity", 1))
        price = int(request.data.get("price_per_unit", 0))
        result = user_item.list_for_sale(quantity=qty, price_per_unit=price)
        if result.get("success"):
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class ItemListingViewSet(viewsets.ModelViewSet):
    """
    /api/listings/           GET list, POST create
    /api/listings/{pk}/      GET retrieve, PUT/PATCH/DELETE
    Actions:
      POST /api/listings/{pk}/buy/   -> buy from listing
    """
    queryset = ItemListing.objects.all()
    serializer_class = ItemListingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=["post"], url_path="buy")
    def buy(self, request, pk=None):
        listing = get_object_or_404(ItemListing, pk=pk)
        qty = int(request.data.get("quantity", 1))
        result = listing.buy_from_listing(request.user, quantity=qty)
        if result.get("success"):
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
