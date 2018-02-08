
from django.conf import settings


PAYEER = getattr(settings, 'PAYEER', {})
