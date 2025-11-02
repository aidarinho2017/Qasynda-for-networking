# members/views/events.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models import Event
from ..permissions.permissions import IsOwnerOrReadOnly
from ..serializers import EventSerializer

from coins.models import CoinTransaction
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date','-time')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        event = serializer.save(organizer=self.request.user)
        profile = self.request.user.profile
        profile.coins += 100
        profile.save()
        CoinTransaction.objects.create(user=self.request.user, amount=100, reason='EVENT_CREATE')