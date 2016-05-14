# from django import http, shortcuts
# from django.conf import settings
# from django.views.generic import View
# from django.contrib import messages
#
# import json
# from utils import helpers
# import models as shop_models
# import forms as order_forms
# import datetime
# import logging
#
# class Checkout(View):
#     def get(self, request, *args, **kwargs):
#         return  shortcuts.render(request, "shop/checkout.html",{
#         'billing_form':order_forms.BillingAddrForm(prefix="bill"),
#         'shipping_form':order_forms.ShippingAddrForm(prefix="ship")
#         })
