from django.contrib import admin

from .models import Game, UserTelegram, ExchangeRate

# Register your models here.
admin.site.register((Game, UserTelegram, ExchangeRate))
