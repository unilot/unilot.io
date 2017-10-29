from django.conf.urls import url
from frontend.views import SubscribeView


urlpatterns = (
    url(r'^$', SubscribeView.as_view(), name='index'),
)
