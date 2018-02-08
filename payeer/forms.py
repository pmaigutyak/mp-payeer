
from django import forms

from payeer.constants import CURRENCIES, LANGUAGES


class MerchantForm(forms.Form):

    order_id = forms.CharField(max_length=255)

    amount = forms.FloatField()

    currency = forms.ChoiceField(choices=CURRENCIES)

    description = forms.CharField()

    language = forms.ChoiceField(choices=LANGUAGES)

    def clean_amount(self):
        return "%.2f" % self.cleaned_data.get('amount')
