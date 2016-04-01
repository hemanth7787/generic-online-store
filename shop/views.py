from django import http, shortcuts
from django.conf import settings
from django.views.generic import View
from django.contrib import messages

import json
from utils import helpers
import models as shop_models
# import forms as shop_forms
import datetime
import logging
# import ipdb

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
                products = products.filter(category=int(request.GET.get('cat')))
            except:
                pass
        categories = shop_models.ProductCategories.objects.all()
        page_no = request.GET.get('page')
        page_size = 10
        queryset = helpers.paginate(products,page_no,page_size)
        return  shortcuts.render(request, "shop/product_list.html",{
        'queryset':queryset,
        'categories':categories,
        })

class ProductDetails(View):
    def get(self, request, *args, **kwargs):
        try:
            product = shop_models.Product.objects.get(pk=kwargs.pop("product_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No product matches the given query.")
        categories = shop_models.ProductCategories.objects.all()
        return  shortcuts.render(request, "shop/product_details.html",{
        'product':product,
        'categories':categories,
        })

# from django.views.decorators.csrf import csrf_exempt



#TODO implement auth check
class BasketAddItem(View):
    ##TODO : Remove csrf overide
    # @csrf_exempt
    # def dispatch(self, request, *args, **kwargs):
    #     return super(BasketAddItem, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            product = shop_models.Product.objects.get(id=request.POST["product_id"])
            prices = product.productprices
        except Exception as expt:
            response_data={"status":"failed", "message":str(expt)}
            return http.HttpResponse(json.dumps(response_data), content_type="application/json")
        # import ipdb; ipdb.set_trace()

        basket, b_obj_created_status = shop_models.Basket.objects.get_or_create(owner=1)
        basket_line, bl_obj_created_status, = shop_models.BasketLine.objects.get_or_create(basket=basket, product=product)
        basket_line.price_excl_tax =  1.00 #TODO : implement tax calculations
        basket_line.price_incl_tax =  prices.selling_price
        basket_line.price_currency = settings.DEFAULT_CURRENCY
        basket_line.save()
        response_data = {"status":"success", "message":"added to cart"}
        return http.HttpResponse(json.dumps(response_data), content_type="application/json")
