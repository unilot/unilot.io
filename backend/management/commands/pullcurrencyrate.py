from django.core.management.base import BaseCommand, CommandError
from coinbase.wallet.client import Client
from sportloto.settings import COINBASE_CONFIG
from backend.models import ExchangeRate


class Command(BaseCommand):
    help = 'Pulls latest exchange rate (ETH -> USD) from coinbase'
    base_currency = 'ETH'
    currencuy = 'USD'

    def handle(self, *args, **options):
        api_client = Client(api_key = COINBASE_CONFIG['API_KEY'], api_secret= COINBASE_CONFIG['API_SECRET'],
                                   api_version= COINBASE_CONFIG['API_VERSION'])
        rate = api_client.get_spot_price(currency_pair = ( '%s-%s' % (self.base_currency, self.currencuy) ) )

        if rate.base == self.base_currency and rate.currency == self.currencuy:
            exchange_rate = ExchangeRate.objects.create(
                base_currency=ExchangeRate.C_CURRENCY_ETH,
                currency = ExchangeRate.CURRENCY_USD,
                rate = float(rate.amount)
            )

            exchange_rate.save()
