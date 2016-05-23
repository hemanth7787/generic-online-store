from django import http, shortcuts
from django.conf import settings
from django.views.generic import View
# from django.contrib import messages
#
# import json
# from utils import helpers
# import models as shop_models
# import forms as order_forms
import datetime
import logging
from order import models as order_models


class CheckoutSummary(View):
    def get(self, request, *args, **kwargs):
        try:
            order_id = self.kwargs['order_id']
        except:
            raise NameError("Error: \"Order\" matching given id not found.")
        order = order_models.Order.objects.get(id=order_id)
        order_lines = order.orderline_set.all()
        return shortcuts.render(request, "shop/checkout_summary.html", {
            "order": order,
            "order_lines" : order_lines
        })
