from django.conf.urls import url, include
from rest_framework import routers
from backend.views import games, devices

router = routers.DefaultRouter()

router.register(r'^games', games.GameViewSet, base_name='games')
router.register(r'^device', devices.DeviceCreateViewSet, base_name='devices   ')

urlpatterns = [
    url(r'^', include(router.urls))
]
