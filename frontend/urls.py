from django.conf.urls import url
from django.views.generic.base import TemplateView


urlpatterns = (
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^about.html$', TemplateView.as_view(template_name='about.html'), name='about_us'),
    url(r'^team.html$', TemplateView.as_view(template_name='team.html'), name='team'),
    url(r'^product.html$', TemplateView.as_view(template_name='product.html'), name='product'),
    url(r'^contact.html$', TemplateView.as_view(template_name='index.html'), name='contact_us')
)
