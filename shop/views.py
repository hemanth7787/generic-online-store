from django import http, shortcuts
from django.conf import settings
from django.views.generic import View
# from django.contrib import messages

import json
from utils import helpers
import models as shop_models
from shop import forms as shop_forms
# import forms as shop_forms
# import datetime
import logging
import ipdb

# globals
if not settings.DEBUG:
    logger = logging.getLogger("django.request")
else:
    logger = logging.getLogger("gs_file")


class ProductsList(View):

    def get(self, request, *args, **kwargs):
        products = shop_models.Product.objects.all()
        if request.GET.get('cat'):
            try:
                products = products.filter(
                    category=int(request.GET.get('cat')))
            except:
                pass
        categories = shop_models.ProductCategories.objects.all()
        page_no = request.GET.get('page')
        page_size = 10
        queryset = helpers.paginate(products, page_no, page_size)
        return shortcuts.render(request, "shop/product_list.html", {
            'queryset': queryset,
            'categories': categories,
        })


class ProductDetails(View):

    def get(self, request, *args, **kwargs):
        try:
            product = shop_models.Product.objects.get(
                pk=kwargs.pop("product_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No product matches the given query.")
        categories = shop_models.ProductCategories.objects.all()
        return shortcuts.render(request, "shop/product_details.html", {
            'product': product,
            'categories': categories,
        })

# from django.views.decorators.csrf import csrf_exempt
# TODO implement auth check


class BasketAddItem(View):

    # TODO : Remove csrf overide
    # @csrf_exempt
    # def dispatch(self, request, *args, **kwargs):
    #     return super(BasketAddItem, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            product = shop_models.Product.objects.get(
                id=request.POST["product_id"])
            prices = product.productprices
        except Exception as expt:
            response_data = {"status": "failed", "message": str(expt)}
            return http.HttpResponse(
                json.dumps(response_data), content_type="application/json")
        # import ipdb; ipdb.set_trace()
        # TODO  insert real user here
        basket, b_obj_created_status = \
            shop_models.Basket.objects.get_or_create(owner=1)
        basket_line, bl_obj_created_status = \
            shop_models.BasketLine.objects.get_or_create(
                basket=basket, product=product)
        basket_line.price_excl_tax = 1.00  # TODO : implement tax calculations
        basket_line.price_incl_tax = prices.selling_price
        basket_line.price_currency = settings.DEFAULT_CURRENCY
        basket_line.save()
        response_data = {"status": "success", "message": "added to cart"}
        return http.HttpResponse(json.dumps(response_data),
                                 content_type="application/json")


class BasketModifyItem(View):

    def post(self, request, *args, **kwargs):
        try:
            basket_line = shop_models.BasketLine.objects.get(
                           id=request.POST["basket_id"])
            # TODO: if request.user ID != basket.owner.id => permission error
            # stock = stock= basket_line.product.productstock.quantity
            if request.POST["action"] == "increment":
                # TODO: check stock if more is avaliable
                basket_line.quantity = basket_line.quantity + 1
                basket_line.save()
            elif request.POST["action"] == "decrement":
                if basket_line.quantity > 1:
                    basket_line.quantity = basket_line.quantity - 1
                    basket_line.save()
                else:
                    raise NameError("only one item, try remove button!")
            elif request.POST["action"] == "remove":
                basket_line.delete()
            else:
                raise NameError("action not defined")
            response_data = {
                "status": "success",
                "message": "added to cart",
                "payload": {
                    "qty": str(basket_line.quantity),
                    "total": str(basket_line.line_total()),
                    "price": str(basket_line.price_incl_tax)
                }
            }
        except Exception as expt:
            response_data = {"status": "failed", "message": str(expt)}
            return http.HttpResponse(json.dumps(response_data),
                                     content_type="application/json")
        return http.HttpResponse(json.dumps(response_data),
                                 content_type="application/json")


class BasketListItems(View):

    def get(self, request, *args, **kwargs):
        # TODO  insert real user here
        basket, b_obj_created_status = \
            shop_models.Basket.objects.get_or_create(owner=1)
        basket_lines = shop_models.BasketLine.objects.filter(basket=basket)

        return shortcuts.render(request, "shop/cart.html", {
            "items": basket_lines
        })


class Checkout(View):

    def get(self, request, *args, **kwargs):
        return shortcuts.render(request, "shop/checkout.html", {
            "billing_form": shop_forms.BillingForm(prefix="bform"),
            "shipping_form": shop_forms.ShippingForm(prefix="sform")
        })

    def post(self, request, *args, **kwargs):
        ipdb.set_trace()
