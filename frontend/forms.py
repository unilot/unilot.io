from django import forms
from django.utils.translation import ugettext as _


class SubscribeForm(forms.Form):
    email = forms.EmailField(required=True, label='', help_text='', widget=forms.EmailInput({
        'placeholder': _('Enter Your Email Address')
    }))


