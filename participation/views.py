from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Participation
from members.models import Event
from coins.models import CoinTransaction
from .serializers import ParticipationSerializer


class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        event_id = request.data.get("event")
        event = Event.objects.get(id=event_id)
        participation, created = Participation.objects.get_or_create(user=request.user, event=event)
        if not created:
            return Response({"detail": "Already participating"}, status=status.HTTP_400_BAD_REQUEST)

        # reward coins
        profile = request.user.profile
        profile.coins += 100
        profile.save()
        CoinTransaction.objects.create(user=request.user, amount=100, reason="PARTICIPATE")
        return Response({"detail": "Joined successfully", "coins": profile.coins})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        participation = self.get_object()
        if participation.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        participation.delete()
        profile = request.user.profile
        profile.coins -= 100
        profile.save()
        CoinTransaction.objects.create(user=request.user, amount=-100, reason="CANCEL")
        return Response({"detail": "Participation cancelled", "coins": profile.coins})