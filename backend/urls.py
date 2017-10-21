from django.conf.urls import url
from backend.views import games, devices

urlpatterns = [
    url(r'^games(|/)$', games.GameViewSet.as_view(), name='games'),
    url(r'^games/(?P<pk>\d+)/prizes', games.GamePrizesViewSet.as_view(), name='games'),
    url(r'^device(|/)$', devices.DeviceCreateViewSet, name='device')
]
