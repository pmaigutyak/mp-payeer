
import base64
import requests

from hashlib import sha256
from urllib import urlencode

from django.core.validators import RegexValidator

from payeer.constants import LANGUAGE_RU
from payeer.forms import MerchantForm
from payeer.settings import PAYEER


__version = '0.1'


class WalletValidator(RegexValidator):
    regex = 'P\d{7,12}$'


class PayeerAPIException(Exception):
    pass


class PayeerApi(object):

    domain = 'https://payeer.com/'
    merchant_url = domain + 'merchant/?'
    api_url = domain + 'ajax/api/api.php'

    def __init__(self, account, api_id, api_pass):

        self._account = account
        self._api_id = api_id
        self._api_pass = api_pass

    @staticmethod
    def validate_wallet(wallet):
        """
        Validates account number
        :param wallet: account number
        :return: bool
        """
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

    def merchant(
            self,
            order_id,
            amount,
            currency,
            description,
            language=None,
            **kwargs):
        """
        Generates merchant request data
        :param order_id:
        :param amount:
        :param currency:
        :param description:
        :param language:
        :param kwargs:
        :return: dict
        """

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

        params.update(kwargs)

        return {
            'location': self.merchant_url + urlencode(params),
            'signature': signature,
            'description': description
        }

    def request_api(self, **params):
        """
        Base api request method
        :param params: api data
        :return: response in json format
        """
        params.update({
            'account': self._account,
            'apiId': self._api_id,
            'apiPass': self._api_pass
        })

        response = requests.post(self.api_url, params).json()

        errors = response.get('errors')

        if errors:
            raise PayeerAPIException(errors)

        return response

    def get_balance(self):
        """
        Check balance
        :return: dict
        """
        return self.request_api(action='balance')['balance']

    def check_user(self, user):
        """
        Checking Existence of Account
        :param user: user's account number in the format P1000000
        :return: True if account exists else False
        """
        try:
            self.request_api(action='checkUser', user=user)
        except PayeerAPIException:
            return False

        return True

    def get_exchange_rate(self, output='N'):
        """
        Automatic Conversion Rates
        :param output: select currencies for conversion rates
               (N - get deposit rates Y - get withdrawal rates)
        :return: dict
        """
        return self.request_api(
            action='getExchangeRate', output=output)['rate']

    def get_pay_systems(self):
        """
        Getting Available Payment Systems
        :return: dict
        """
        return self.request_api(action='getPaySystems')['list']

    def get_history_info(self, history_id):
        """
        Getting Information about a Transaction
        :param history_id: transaction ID
        :return: dict
        """
        return self.request_api(
            action='historyInfo', historyId=history_id)['info']

    def shop_order_info(self, shop_id, order_id):
        """
        Information on a Store Transaction
        :param shop_id: merchant ID (m_shop)
        :param order_id: transaction ID in your accounting system (m_orderid)
        :return: dict
        """
        return self.request_api(
            action='shopOrderInfo', shopId=shop_id, orderId=order_id)

    def transfer(
            self,
            sum,
            to,
            cur_in='USD',
            cur_out='USD',
            comment=None,
            protect=None,
            protect_period=None,
            protect_code=None):

        self.validate_wallet(to)

        data = {
            'action': 'transfer',
            'sum': sum,
            'to': to,
            'curIn': cur_in,
            'curOut': cur_out
        }

        if comment is not None:
            data['comment'] = comment

        if protect is not None:
            data['protect'] = protect

            if protect_period is not None:
                data['protectPeriod'] = protect_period

            if protect_code is not None:
                data['protectCode'] = protect_code

        response = self.request_api(**data)

        if response.get('historyId', 0) > 0:
            return True
        else:
            return False

    def check_output(
            self,
            ps,
            ps_account,
            sum_in,
            cur_in='USD',
            cur_out='USD'):
        """
        Checking Possibility of Payout
        This method allows you to check the possibility of a payout without actually creating a payout
        (you can get the withdrawal/reception amount or check errors in parameters)
        :param ps: ID of selected payment system
        :param ps_account: recipient's account number in the selected payment system
        :param sum_in: amount withdrawn (the amount deposited will be calculated automatically, factoring in all fees from the recipient)
        :param cur_in: currency with which the withdrawal will be performed
        :param cur_out: deposit currency
        :return: True if the payment is successful
        """
        data = {
            'action': 'initOutput',
            'ps': ps,
            'param_ACCOUNT_NUMBER': ps_account,
            'sumIn': sum_in,
            'curIn': cur_in,
            'curOut': cur_out
        }
        try:
            self.request_api(**data)
        except PayeerAPIException:
            return False

        return True

    def output(self, ps, ps_account, sum_in, cur_in='USD', cur_out='USD'):
        """
        Payout
        :param ps: ID of selected payment system
        :param ps_account: recipient's account number in the selected payment system
        :param sum_in: amount withdrawn (the amount deposited will be calculated automatically, factoring in all fees from the recipient)
        :param cur_in: currency with which the withdrawal will be performed
        :param cur_out: deposit currency
        :return:
        """
        data = {
            'action': 'output',
            'ps': ps,
            'param_ACCOUNT_NUMBER': ps_account,
            'sumIn': sum_in,
            'curIn': cur_in,
            'curOut': cur_out
        }
        return self.request_api(**data)

    def history(self, **params):
        """
        History of transactions
        :param sort: sorting by date (asc, desc)
        :param count: count of records (max 1000)
        :param from: begin of the period
        :param to: end of the period
        :param type: transaction type
            (incoming - incoming payments, outgoing - outgoing payments)
        :param append: id of the previous transaction
        :return:
        """
        params['action'] = 'history'

        return self.request_api(**params)['history']


payeer_api = PayeerApi(
    account=PAYEER.get('ACCOUNT'),
    api_id=PAYEER.get('API_ID'),
    api_pass=PAYEER.get('API_PASS'))
