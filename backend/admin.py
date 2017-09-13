from django.contrib import admin

from .models import Game, UserTelegram, Device, ExchangeRate

# Register your models here.
admin.site.register((Game, UserTelegram, Device, ExchangeRate))
