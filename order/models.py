from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import logging
import datetime

from shop import models as shop_models
#globals
if not settings.DEBUG:
    logger = logging.getLogger("django.request")
else:
    logger = logging.getLogger("gs_file")


class Order(models.Model):
    STATUS_LEVELS =  (('C', 'Created',),('P', 'Payed',))
    user = models.ForeignKey(User)
    basket = models.ForeignKey(shop_models.Basket)
    billing_address = models.ForeignKey("BillingAddress", blank=True, null=True)
    shiping_address = models.ForeignKey("ShippingAddress")
    bill_same_as_ship = models.BooleanField(default=False)
    order_number = models.CharField(max_length=128)
    currency = models.CharField(max_length=16)
    total_excl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    total_incl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_incl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_excl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_method = models.CharField(max_length=128)
    shipping_code = models.CharField(max_length=128)
    status = models.CharField(max_length=8, default=STATUS_LEVELS[0][0])
    guest_email = models.CharField(max_length=128)
    date_created = models.DateTimeField()

class BillingAddress(models.Model):
    addr_user = models.ForeignKey(User)
    addr = models.OneToOneField(shop_models.Address)
    date_created = models.DateTimeField(default=datetime.datetime.now)

class ShippingAddress(models.Model):
    addr_user = models.ForeignKey(User)
    addr = models.OneToOneField(shop_models.Address)
    notes = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)

class OrderLine(models.Model):
    order = models.ForeignKey("Order")
    product = models.ForeignKey(shop_models.Product)
    # line_reference = models.CharField(max_length=128)
    quantity = models.PositiveSmallIntegerField(default=1)
    price_excl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    price_incl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    price_currency = models.CharField(max_length=16, null=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    serial_number = models.CharField(max_length=128, null=True)
    status_message = models.CharField(max_length=255, null=True)
    est_date = models.DateField(null=True)
    # In case of offers
    # unit_cost_price
    # unit_price_incl_tax
    # unit_price_excl_tax
    # unit_retail_price
    def line_total(self):
        return self.quantity * self.price_incl_tax



class Transaction(models.Model):
    order = models.ForeignKey(Order)
    txn_type = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reference = models.CharField(max_length=128)
    status  = models.CharField(max_length=128)
    date_created = models.DateTimeField()

class PaymentSource(models.Model):
    order = models.ForeignKey(Order)
    amount_allocated = models.DecimalField(max_digits=8, decimal_places=2)
    amount_debited = models.DecimalField(max_digits=8, decimal_places=2)
    amount_refunded = models.DecimalField(max_digits=8, decimal_places=2)

    reference = models.CharField(max_length=128)
    label = models.CharField(max_length=128)
    currency = models.CharField(max_length=16)
