from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Game, UserTelegram, ExchangeRate


def add_bet_tracking(modeladmin, request, queryset):
    """
    :param modeladmin:
    :type django.contrib.admin.options.ModelAdmin:
    :param request:
    :type django.http.request.HttpRequest:
    :param queryset:
    :type django.db.models.query.QuerySet:
    :return:
    """
    games = queryset.all()

    for game in games:
        game.add_bet_tracking(True, True)

add_bet_tracking.short_description = _('Add bet tracking to models')

class GameAdmin(admin.ModelAdmin):
    actions = [add_bet_tracking]

admin.site.register((UserTelegram, ExchangeRate))
admin.site.register(Game, GameAdmin)
