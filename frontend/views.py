from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from frontend.forms import SubscribeForm
from frontend.utils.mailchimp import AppMailchimp
from backend import models


class SubscribeView(FormView):
    template_name = 'index.html'
    form_class = SubscribeForm
    success_url = '/'
    success_message = _('Email successfully saved.')

    def form_valid(self, form):
        try:
            #Subscribe
            mailchimp = AppMailchimp.get_instance()

            mailchimp.lists.members.create(list_id='edc257a0af', data={
                'email_address': form.cleaned_data['email'],
                'status': 'subscribed'
            })

            return super(SubscribeView, self).form_valid(form)
        except Exception as e:
            form.add_error('email', _('Subscription failed. Email might already exist in database.'))
            return self.form_invalid(form)


# Mobile views
class MobileFAQListView(ListView):
    model = models.FAQ
    template_name = 'mobile/faq.html'
