# comments/serializers.py
from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'event', 'owner', 'owner_username', 'message', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
