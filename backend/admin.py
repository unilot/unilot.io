from django.contrib import admin
from django.utils.translation import ugettext as _
from martor.widgets import AdminMartorWidget
from django.db import models as django_models
from hvad.admin import TranslatableAdmin

from . import models


class FAQAdmin(TranslatableAdmin):
    list_display = ('question_',)

    formfield_overrides = {
        django_models.TextField: {'widget': AdminMartorWidget}
    }

admin.site.register((models.Game, models.UserTelegram, models.ExchangeRate, models.DeviceSettings))
admin.site.register(models.FAQ, FAQAdmin)
