# MP-Payeer

Django payeer integration app.

### Installation

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

## Usage example
```
from payeer.api import payeer_api
from payeer.constants import CURRENCY_USD

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

### Requirements

App require this packages:
* django

### Donators
* Andriy Onishchuk
