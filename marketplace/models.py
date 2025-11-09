from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from items.models import Item


class Listing(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_listings")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.seller.username} sells {self.item.name} x{self.quantity} for {self.price_per_unit} each"

    def buy_from_listing(self, buyer, quantity):
        from coins.models import CoinTransaction
        from users.models import UserProfile

        if quantity <= 0 or quantity > self.quantity:
            return {"success": False, "message": "Invalid quantity"}

        total_cost = self.price_per_unit * quantity

        with transaction.atomic():
            buyer_profile = UserProfile.objects.select_for_update().get(user=buyer)
            seller_profile = UserProfile.objects.select_for_update().get(user=self.seller)

            if buyer_profile.coins < total_cost:
                return {"success": False, "message": "Insufficient coins"}

            # Transfer coins
            buyer_profile.coins -= total_cost
            seller_profile.coins += total_cost
            buyer_profile.save()
            seller_profile.save()

            # Record transactions
            CoinTransaction.objects.create(user=buyer, amount=-total_cost, reason="PARTICIPATE")  # or new reason
            CoinTransaction.objects.create(user=self.seller, amount=total_cost, reason="PARTICIPATE")

            # Add to buyer's inventory
            from items.models import UserItem
            buyer_item, _ = UserItem.objects.get_or_create(user=buyer, item=self.item)
            buyer_item.quantity += quantity
            buyer_item.save()

            # Update listing
            self.quantity -= quantity
            if self.quantity == 0:
                self.delete()
            else:
                self.save()

            return {"success": True, "message": "Purchased from listing", "coins": buyer_profile.coins}
