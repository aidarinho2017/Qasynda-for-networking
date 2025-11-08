# items/admin.py
from django.contrib import admin
from .models import Item, UserItem

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "cost", "available_quantity", "created_at")
    search_fields = ("name", "type")
    list_filter = ("type",)

@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item", "quantity", "created_at")
    search_fields = ("user__username", "item__name")
