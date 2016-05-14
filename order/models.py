from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import logging

from shop import models as shop_models
#globals
if not settings.DEBUG:
    logger = logging.getLogger("django.request")
else:
    logger = logging.getLogger("gs_file")


class Order(models.Model):
    user = models.ForeignKey(User)
    basket = models.ForeignKey(shop_models.Basket)
    billing_address = models.ForeignKey("BillingAddress")
    shiping_address = models.ForeignKey("ShippingAddress")
    order_number = models.CharField(max_length=128)
    currency = models.CharField(max_length=16)
    total_excl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    total_incl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_incl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_excl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_method = models.CharField(max_length=128)
    shipping_code = models.CharField(max_length=128)
    status = models.CharField(max_length=128)
    guest_email = models.CharField(max_length=128)
    date_created = models.DateTimeField()

class BillingAddress(models.Model):
    addr_user = models.ForeignKey(User)
    addr = models.OneToOneField(shop_models.Address)

class ShippingAddress(models.Model):
    addr_user = models.ForeignKey(User)
    addr = models.OneToOneField(shop_models.Address)
    notes = models.TextField()

class OrderLine(models.Model):
    order = models.ForeignKey("Order")
    vendor = models.ForeignKey(shop_models.Vendors)
    product = models.ForeignKey(shop_models.Product)
    # line_reference = models.CharField(max_length=128)
    quantity = models.PositiveSmallIntegerField()
    price_excl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    price_incl_tax = models.DecimalField(max_digits=8, decimal_places=2)
    price_currency = models.CharField(max_length=16)
    date_created = models.DateTimeField()
    serial_number = models.CharField(max_length=128)
    status_message = models.CharField(max_length=255)
    est_date = models.DateField()
    # In case of offers
    # unit_cost_price
    # unit_price_incl_tax
    # unit_price_excl_tax
    # unit_retail_price

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
