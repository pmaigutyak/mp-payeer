
import base64
from hashlib import sha256
from urllib import urlencode

from django.core.validators import RegexValidator

from payeer.constants import LANGUAGE_RU
from payeer.forms import MerchantForm
from payeer.settings import PAYEER


__version = '0.1'


class WalletValidator(RegexValidator):
    regex = 'P\d{7,12}$'


class PayeerApi(object):

    merchant_url = 'https://payeer.com/merchant/?'

    def __init__(self, account, api_id, api_pass):

        self._account = account
        self._api_id = api_id
        self._api_pass = api_pass

    @staticmethod
    def validate_wallet(wallet):
        validator = WalletValidator()
        validator(wallet)

    @staticmethod
    def generate_description(description):
        return base64.b64encode(description.encode('utf-8')).decode('utf-8')

    def generate_signature(self, order_id, amount, currency, description):

        options = [
            self._api_id,
            order_id,
            amount,
            currency,
            description,
            self._api_pass
        ]

        hash_str = sha256(':'.join(options).encode())

        return hash_str.hexdigest().upper()

    def generate_merchant_url(
            self,
            order_id,
            amount,
            currency,
            description,
            language=None):

        self.validate_wallet(self._account)

        if language is None:
            language = PAYEER.get('LANGUAGE', LANGUAGE_RU)

        form = MerchantForm({
            'order_id': order_id,
            'amount': amount,
            'currency': currency,
            'description': description,
            'language': language
        })

        form.is_valid()

        data = form.cleaned_data

        desc_str = self.generate_description(data['description'])

        signature = self.generate_signature(
            data['order_id'], data['amount'], data['currency'], desc_str)

        params = {
            'm_shop': self._api_id,
            'm_orderid': data['order_id'],
            'm_amount': data['amount'],
            'm_curr': data['currency'],
            'm_desc': desc_str,
            'm_sign': signature,
            'lang': data['language']
        }

        return self.merchant_url + urlencode(params)


payeer_api = PayeerApi(
    account=PAYEER.get('ACCOUNT'),
    api_id=PAYEER.get('API_ID'),
    api_pass=PAYEER.get('API_PASS'))
