# MP-Payeer

Django payeer integration app.
Official docs: https://payeercom.docs.apiary.io

## Installation

Install with pip:
```
$ pip install django-payeer
```

App settings:
```
PAYEER = {
    'ACCOUNT': 'P1000000',
    'API_ID': '12345',
    'API_PASS': 'qwerty',
    'LANGUAGE': 'en' # optional, default: 'ru'
}
```

## Usage
```
from payeer.api import payeer_api
from payeer.constants import CURRENCY_USD
```
### Merchant
```
data = payeer_api.merchant(
        order_id=123,
        amount=10,
        currency=CURRENCY_USD,
        description='Test')
```
payeer_api.merchant returns:
```
{
    'location': '...', # redirect url
    'signature': '...', # generated signature
    'description': '...' # generated description
}
```
### Balance Check
Obtain wallet balance.
```
payeer_api.get_balance()
```
### Checking Existence of Account
You can check the existence of an account number prior to transfer in the Payeer system.
```
payeer_api.check_user('P1000000')
```
### Automatic Conversion Rates
If during deposit/transfer/withdrawal the withdrawal currency curIn is different from the receiving currency curOut, the amount will be converted based on Payeer’s internal echange rates, which can be obtained using the following method.

(N - get deposit rates Y - get withdrawal rates)
```
payeer_api.get_exchange_rate('Y')
```
### Getting Available Payment Systems
This method returns a list of payment systems that are available for payout.
```
payeer_api.get_pay_systems()
```

## Requirements
App require this packages:
* django

## Donators
* Andriy Onishchuk
