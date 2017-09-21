from rest_framework import viewsets
from oauth2_provider.contrib.rest_framework import TokenHasScope
from backend.models import Game
from backend.serializers.game import PublicGameSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset = Game.filter_active().all()
    serializer_class = PublicGameSerializer
