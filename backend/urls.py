from django.conf.urls import url
from backend.views import games, devices
from sportloto.settings import DEBUG

urlpatterns = [
    url(r'^games(|/)$', games.GamesView.as_view(), name='games'),
    url(r'^games/(?P<pk>\d+)(|/)$', games.SingleGameView.as_view(), name='game'),
    url(r'^games/archived(|/)$', games.GameArchivedView.as_view(), name='games_archived'),
    url(r'^games/(?P<pk>\d+)/winners(|/)$', games.GamePrizesView.as_view(), name='game_winners'),
    url(r'^device(|/)$', devices.DeviceCreateView.as_view(), name='device')
]

if DEBUG:
    urlpatterns += [
        url(r'^games/(?P<pk>\d+)/push(|/)$', games.GameDebugPushView.as_view(), name='game_push')
    ]
