from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import logging
import datetime
import uuid
import os

#globals
if not settings.DEBUG:
    logger = logging.getLogger("django.request")
else:
    logger = logging.getLogger("gs_file")


class ProductCategories(models.Model):
    parent = models.ForeignKey('self', null = True, related_name = "parent_for")
    title = models.CharField(max_length = 255)
    slug = models.SlugField()
    parent_slug = models.SlugField()
    depth = models.PositiveSmallIntegerField()
    def __unicode__(self):
        return self.title

class Product(models.Model):
    category =  models.ForeignKey('ProductCategories')
    vendor = models.ForeignKey('Vendors')
    # vendor = models.ForeignKey('Vendors')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_added = models.DateTimeField()
    track_stock  = models.BooleanField()
    requires_shipping = models.BooleanField()
    serial_number = models.CharField(max_length=128)
    #Uniquely determines a product by diffrent vendors UPC  universal
    product_code = models.CharField(max_length=128)

def unique_image_name(instance, filename):
    upload_date = datetime.datetime.today()
    formatted_date = upload_date.strftime("%B_%Y")
    return '/'.join(['product_images',formatted_date, str(uuid.uuid4())+os.path.splitext(filename)[1]])

class ProductImages(models.Model):
    product =  models.ForeignKey('Product')
    caption = models.CharField(max_length=128)
    display_order = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to=unique_image_name, null=True)


class ProductStock(models.Model):
    product = models.OneToOneField('Product')
    quantity = models.PositiveSmallIntegerField()
    reorder_point = models.PositiveSmallIntegerField()
    reorder_quantity = models.PositiveSmallIntegerField()

class ProductPrices(models.Model):
    product = models.OneToOneField('Product')
    vendor_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(default=datetime.datetime.now)
    #"stockrecord_id" integer NULL REFERENCES "partner_stockrecord" ("id"));

class Vendors(models.Model):
    user = models.ForeignKey(User)
    code = models.CharField(max_length=128, unique = True)
    name = models.CharField(max_length=128)
    def __unicode__(self):
        return self.name

class VendorAddress(models.Model):
    vendor = models.ForeignKey('Vendors')
    addr = models.OneToOneField('Address',null=True)

class Address(models.Model):
    title = models.CharField(max_length=64) # MR, MRs
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255)
    line3 = models.CharField(max_length=255)
    line4 = models.CharField(max_length=255)
    phone = models.CharField(max_length=16)
    state = models.CharField(max_length=255)
    postcode = models.CharField(max_length=64)
    # country = models.ForeignKey('country') #TODO

class Basket(models.Model):
    owner = models.OneToOneField(User)
    status = models.CharField(max_length=128,default="OPEN")
    date_created = models.DateTimeField(default=datetime.datetime.now)
    date_updated = models.DateTimeField(default=datetime.datetime.now)
    date_submitted = models.DateTimeField(null=True)

class BasketLine(models.Model):
    basket = models.ForeignKey("Basket")
    product = models.ForeignKey("Product")
    # line_reference = models.CharField(max_length=128)
    quantity = models.PositiveSmallIntegerField(default=1)
    price_excl_tax = models.DecimalField(max_digits=8, decimal_places=2,default=0.00)
    price_incl_tax = models.DecimalField(max_digits=8, decimal_places=2,default=0.00)
    price_currency = models.CharField(max_length=16, null=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    #UNIQUE ("basket_id","line_reference"));
    def line_total(self):
        return self.quantity * self.price_incl_tax
