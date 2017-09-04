from django.conf.urls import url, include
from rest_framework import routers
from backend.views import games

router = routers.DefaultRouter()

router.register(r'^games', games.GameViewSet, base_name='games')

urlpatterns = [
    url(r'^', include(router.urls))
]
