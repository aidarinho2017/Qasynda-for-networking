# items/models.py
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.urls import reverse
import hashlib
import urllib.parse

# If you prefer emojis for small icons, we keep a mapping below.


def deterministic_image_url(seed: str, size: int = 400) -> str:
    """
    Deterministic "random" image URL for an item based on a seed string:
      - Uses picsum.photos with a seed derived from item name to produce repeatable images.
      - As fallback (if you don't want external images), you can use emojis in frontend.
    """
    h = hashlib.sha1(seed.encode("utf-8")).hexdigest()
    # Use the hex as a "seed" quirk to pick an image ID via modulo
    img_id = int(h[:8], 16) % 1000  # picsum has many images; this keeps it stable
    return f"https://picsum.photos/seed/{urllib.parse.quote(h)}/{size}/{size}"


class Item(models.Model):
    TYPE_CHOICES = [
        ("badge", "Badge"),
        ("booster", "Booster"),
        ("coin", "Coin"),
        ("token", "Token"),
        ("item", "Item"),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="item")
    cost = models.IntegerField(default=0)  # price in qasynda_coins
    available_quantity = models.PositiveIntegerField(default=0)  # remaining supply
    image_url = models.CharField(max_length=500, blank=True, help_text="Auto-generated if empty.")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.type})"

    def save(self, *args, **kwargs):
        # If image_url is empty, generate deterministic image URL using name+id (id may be None before first save)
        if not self.image_url:
            seed = self.name
            # If object already has a primary key include it to further diversify
            if self.pk:
                seed = f"{seed}-{self.pk}"
            self.image_url = deterministic_image_url(seed)
        super().save(*args, **kwargs)

    def buy(self, user, quantity=1):
        """
        Business logic to buy `quantity` items for `user`.
        Returns dict { success: bool, message: str, coins: new_balance }.
        This method is atomic and will create a CoinTransaction and UserItem accordingly.
        """
        from coins.models import CoinTransaction  # local import to avoid circular problems
        from users.models import UserProfile

        if quantity <= 0:
            return {"success": False, "message": "Quantity must be > 0"}

        total_cost = self.cost * quantity

        with transaction.atomic():
            profile = UserProfile.objects.select_for_update().get(user=user)

            if profile.coins < total_cost:
                return {"success": False, "message": "Insufficient coins"}

            if self.available_quantity < quantity:
                return {"success": False, "message": "Not enough items available"}

            # Deduct coins
            profile.coins -= total_cost
            profile.save()

            # Update available quantity
            self.available_quantity -= quantity
            self.save()

            # Record coin transaction
            CoinTransaction.objects.create(user=user, amount=-total_cost, reason="EVENT_CREATE" if self.type == "badge" else "PARTICIPATE")

            # Add to user's inventory
            user_item, _ = UserItem.objects.get_or_create(user=user, item=self)
            user_item.quantity += quantity
            user_item.save()

            return {"success": True, "message": "Purchased", "coins": profile.coins}

    def sell_back(self, user, quantity=1, sell_price: int | None = None):
        """
        Sell item back to system. `sell_price` per item (if None, use cost * 0.5 fallback).
        Returns dict { success, message, coins }.
        """
        from coins.models import CoinTransaction
        from users.models import UserProfile

        if quantity <= 0:
            return {"success": False, "message": "Quantity must be > 0"}

        if sell_price is None:
            # default 50% back to user
            sell_price = int(self.cost * 0.5)

        with transaction.atomic():
            try:
                user_item = UserItem.objects.select_for_update().get(user=user, item=self)
            except UserItem.DoesNotExist:
                return {"success": False, "message": "You do not own this item"}

            if user_item.quantity < quantity:
                return {"success": False, "message": "You don't have enough quantity to sell"}

            profile = UserProfile.objects.select_for_update().get(user=user)

            # Reduce user's item count
            user_item.quantity -= quantity
            if user_item.quantity == 0:
                user_item.delete()
            else:
                user_item.save()

            # Increase system pool
            self.available_quantity += quantity
            self.save()

            # Credit coins to user
            total_credit = sell_price * quantity
            profile.coins += total_credit
            profile.save()

            CoinTransaction.objects.create(user=user, amount=total_credit, reason="CANCEL")

            return {"success": True, "message": "Sold back", "coins": profile.coins}


class UserItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="owners")
    quantity = models.PositiveIntegerField(default=0)
    purchase_price = models.IntegerField(null=True, blank=True, help_text="Optional: price paid per unit")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "item")

    def __str__(self):
        return f"{self.user.username} — {self.item.name} x{self.quantity}"
