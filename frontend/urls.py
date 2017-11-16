from django.conf.urls import url
from frontend import views


urlpatterns = (
    url(r'^$', views.SubscribeView.as_view(), name='index'),
    url(r'^mobile/faq(|/)$', views.MobileFAQListView.as_view(), name='mobile_faq'),
)
