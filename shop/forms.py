from django import forms
from shop import models as shop_models

class ShippingForm(forms.ModelForm):
    pass

    class Meta:
        model = shop_models.Address
        fields = ["title", "first_name", "last_name", "line1", "line2",
                  "line3", "line4", "phone", "state", "postcode"]


class BillingForm(forms.ModelForm):
    same_as_shipping_address = forms.BooleanField(required=False)

    class Meta:
        model = shop_models.Address
        fields = [ "same_as_shipping_address", "title", "first_name", "last_name", "line1", "line2",
                  "line3", "line4", "phone", "state", "postcode"]
