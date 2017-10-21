from django.conf.urls import url
from backend.views import games, devices

urlpatterns = [
    url(r'^games(|/)$', games.GamesView.as_view(), name='games'),
    url(r'^games/(?P<pk>\d+)/winners(|/)$', games.GamePrizesView.as_view(), name='games'),
    url(r'^device(|/)$', devices.DeviceCreateViewSet, name='device')
]
