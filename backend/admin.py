from django.contrib import admin

from .models import Game, UserTelegram, Device

# Register your models here.
admin.site.register((Game, UserTelegram, Device))
