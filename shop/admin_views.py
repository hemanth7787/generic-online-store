from django.shortcuts import render
from django import http
import logging
from django.conf import settings
from django.views.generic import View
import shop.admin_forms as shop_forms
import shop.models as shop_models
from django import shortcuts
from django.contrib import messages
import datetime
from utils import helpers
import ipdb

# globals
if not settings.DEBUG:
    logger = logging.getLogger("django.request")
else:
    logger = logging.getLogger("gs_file")

class ProductsAdmin(View):
    def get(self, request, *args, **kwargs):
        table = dict()
        table['headers'] = ["Name", "Product Code", "Serial number", "Date", "Actions"]
        table['fields'] = ["name", "product_code", "serial_number", "date_added", "admin/shop/product_table_actions.html"]

        product_list = shop_models.Product.objects.all()
        page_no = request.GET.get('page')
        page_size = 10
        table["data"] = helpers.paginate(product_list,page_no,page_size)

        return  render(request, "admin/shop/products.html",{
        'table':table,
        })

class ProductsCreate(View):
    def get(self, request, *args, **kwargs):
        form = shop_forms.ProductForm()
        product_image_form = shop_forms.ProductImageForm()
        product_price_form = shop_forms.ProductPriceAndStockForm()
        return  render(request, "admin/shop/products_create.html",{
            'formbundle':[
            ("Product details",form),
            ("Product image",product_image_form),
            ("Price and stock",product_price_form)],
        })
    def post(self, request, *args, **kwargs):
        product_image_form = shop_forms.ProductImageForm(request.POST, request.FILES)
        form = shop_forms.ProductForm(request.POST)
        product_price_form = shop_forms.ProductPriceAndStockForm(request.POST)
        if form.is_valid() and product_image_form.is_valid() and product_price_form.is_valid():
            product = shop_models.Product()
            product.vendor = form.cleaned_data['vendor']
            product.name = form.cleaned_data['name']
            product.serial_number = form.cleaned_data['serial_number']
            product.description = form.cleaned_data['description']
            product.category = form.cleaned_data['category']
            product.product_code = form.cleaned_data['product_code']
            product.track_stock = product_price_form.cleaned_data['track_stock']
            product.requires_shipping = product_price_form.cleaned_data['require_shipping']
            product.date_added = datetime.datetime.now()
            product.save()

            for i in range(1,product_image_form.count):
                if request.FILES.has_key('image'+str(i)):
                    product_image = shop_models.ProductImages(
                        product = product,
                        caption = product_image_form.cleaned_data["caption"+str(i)] or "NC",
                        display_order = product_image_form.cleaned_data["display_order"+str(i)] or product_image_form.count,
                        image = request.FILES['image'+str(i)]
                    )
                    product_image.save()

            stock = shop_models.ProductStock()
            stock.product = product
            stock.quantity = product_price_form.cleaned_data['quantity_in_stock']
            stock.reorder_point = product_price_form.cleaned_data['reorder_point']
            stock.reorder_quantity = product_price_form.cleaned_data['reorder_quantity']
            stock.save()

            price = shop_models.ProductPrices()
            price.product = product
            price.vendor_price =  product_price_form.cleaned_data['vendor_price']
            price.selling_price =  product_price_form.cleaned_data['selling_price']
            price.discount_price =  product_price_form.cleaned_data['discount_price']
            price.save()

            messages.success(request, 'Save successful..')
            return shortcuts.redirect("admin_shop_products")
        else:
            messages.error(request, 'Product not saved..')
        return  render(request, "admin/shop/products_create.html",{
            'formbundle':[
            ("Product details",form),
            ("Product image",product_image_form),
            ("Price and stock",product_price_form)],
        })

class ProductsEdit(View):
    def get(self, request, *args, **kwargs):
        try:
            product = shop_models.Product.objects.get(pk=kwargs.pop("product_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No product matches the given query.")

        form = shop_forms.ProductForm(initial={
            'category' : product.category,
            'vendor' : product.vendor,
            'name' : product.name,
            'product_code' : product.product_code,
            'serial_number' : product.serial_number,
            'description' : product.description
        })
        product_images = product.productimages_set.all()
        data = {}
        for i in range(0,len(product_images)):
            data['caption'+str(i+1)] = product_images[i].caption
            data['display_order'+str(i+1)] = product_images[i].display_order
            data['image'+str(i+1)] = product_images[i].image
            data['image'+str(i+1)+'_pk'] = product_images[i].id
        product_image_form = shop_forms.ProductImageForm(initial=data)
        stock = product.productstock
        price = product.productprices
        product_price_form = shop_forms.ProductPriceAndStockForm(initial={
            'vendor_price' : price.vendor_price,
            'selling_price' : price.selling_price,
            'discount_price' : price.discount_price,
            'quantity_in_stock' : stock.quantity,
            'reorder_point' : stock.reorder_point,
            'reorder_quantity' : stock.reorder_quantity,
            'track_stock' : product.track_stock,
            'require_shipping' : product.requires_shipping,
        })

        return  render(request, "admin/shop/products_edit.html",{
            'formbundle':[
            ("Product details",form),
            ("Product image",product_image_form),
            ("Price and stock",product_price_form)],
        })
    def post(self, request, *args, **kwargs):
        try:
            product = shop_models.Product.objects.get(pk=kwargs.pop("product_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No product matches the given query.")
        product_image_form = shop_forms.ProductImageForm(request.POST, request.FILES)
        form = shop_forms.ProductForm(request.POST)
        product_price_form = shop_forms.ProductPriceAndStockForm(request.POST)
        if form.is_valid() and product_image_form.is_valid() and product_price_form.is_valid():
            product.name = form.cleaned_data['name']
            product.serial_number = form.cleaned_data['serial_number']
            product.description = form.cleaned_data['description']
            product.category = form.cleaned_data['category']
            product.vendor = form.cleaned_data['vendor']
            product.product_code = form.cleaned_data['product_code']
            product.track_stock = product_price_form.cleaned_data['track_stock']
            product.requires_shipping = product_price_form.cleaned_data['require_shipping']
            product.date_added = datetime.datetime.now()
            product.save()

            #  Save , update or delete images
            #  imagex_pk(int), image(file), imagex-clear(bool) Form fields are in consideration
            #  0                 1                X       -> New image
            #  1                 0                0       -> Update details only
            #  1                 0                1       -> Delete existing image
            #  1                 1                X       -> Update existing image and details

            for i in range(1,product_image_form.count):
                if request.FILES.has_key('image'+str(i)) and request.POST['image'+str(i)+'_pk'] == "":
                    # New image added
                    product_image = shop_models.ProductImages(
                        product = product,
                        caption = product_image_form.cleaned_data["caption"+str(i)] or "NC",
                        display_order = product_image_form.cleaned_data["display_order"+str(i)] or product_image_form.count,
                        image = request.FILES['image'+str(i)]
                    )
                    product_image.save()
                elif request.FILES.has_key('image'+str(i)) and request.POST['image'+str(i)+'_pk'] != "":
                    # Update existing image
                    product_image = shop_models.ProductImages.objects.get(pk=product_image_form.cleaned_data['image'+str(i)+'_pk'])
                    product_image.caption = product_image_form.cleaned_data["caption"+str(i)] or "NC"
                    product_image.display_order = product_image_form.cleaned_data["display_order"+str(i)] or product_image_form.count
                    product_image.image = request.FILES['image'+str(i)]
                    product_image.save()
                elif  request.POST.has_key("image"+str(i)+"-clear") and not request.FILES.has_key('image'+str(i)) and request.POST['image'+str(i)+'_pk'] != "":
                    # Delete  existing image
                    shop_models.ProductImages.objects.get(pk=request.POST['image'+str(i)+'_pk']).delete()
                elif not request.POST.has_key("image"+str(i)+"-clear") and not request.FILES.has_key('image'+str(i)) and request.POST['image'+str(i)+'_pk'] != "":
                    # Update details without touching image
                    product_image = shop_models.ProductImages.objects.get(pk=product_image_form.cleaned_data['image'+str(i)+'_pk'])
                    product_image.caption = product_image_form.cleaned_data["caption"+str(i)] or "NC"
                    product_image.display_order = product_image_form.cleaned_data["display_order"+str(i)] or product_image_form.count
                    product_image.save()
                else:
                    pass

            stock = shop_models.ProductStock.objects.get(product=product)
            stock.quantity = product_price_form.cleaned_data['quantity_in_stock']
            stock.reorder_point = product_price_form.cleaned_data['reorder_point']
            stock.reorder_quantity = product_price_form.cleaned_data['reorder_quantity']
            stock.save()

            price = shop_models.ProductPrices.objects.get(product=product)
            price.vendor_price =  product_price_form.cleaned_data['vendor_price']
            price.selling_price =  product_price_form.cleaned_data['selling_price']
            price.discount_price =  product_price_form.cleaned_data['discount_price']
            price.save()

            messages.success(request, 'Update successful..')
            return shortcuts.redirect("admin_shop_products")
        else:
            messages.error(request, 'Product not updated..')
        return  render(request, "admin/shop/products_edit.html",{
            'formbundle':[
            ("Product details",form),
            ("Product image",product_image_form),
            ("Price and stock",product_price_form)],
        })

class ProductsDelete(View):
    def get(self, request, *args, **kwargs):
        try:
            product = shop_models.Product.objects.get(pk=kwargs.pop("product_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No product matches the given query.")
        try:
            product.productimages_set.all().delete()
            product.productprices.delete()
            product.productstock.delete()
            product.delete()
        except:
            return http.JsonResponse({'status': 'failed'})
        return http.JsonResponse({'status': 'success'})



class CategoryAdmin(View):
    def get(self, request, *args, **kwargs):
        table = dict()
        table['headers'] = ["Title", "Slug", "Depth", "Parent","Actions"]
        table['fields'] = ["title", "slug", "depth", "parent", "admin/shop/category_table_actions.html"]
        category_list = shop_models.ProductCategories.objects.all()
        page_no = request.GET.get('page')
        page_size = 10
        table["data"] = helpers.paginate(category_list,page_no,page_size)

        return  render(request, "admin/shop/categories.html",{
        'table':table,
        })

class CategoriesCreate(View):
    def get(self, request, *args, **kwargs):
        form = shop_forms.ProductCategoryForm()
        return  render(request, "admin/shop/categories_create.html",{
            'formbundle':[
            ("Category details",form),]
        })
    def post(self, request, *args, **kwargs):
        form = shop_forms.ProductCategoryForm(request.POST)
        if form.is_valid():
            category_data = form.save(commit=False) #Modelform
            category_data.parent_slug =  category_data.parent.slug
            category_data.save()

            messages.success(request, 'Save successful..')
            return shortcuts.redirect("admin_shop_categories")
        else:
            messages.error(request, 'Product not saved..')
        return  render(request, "admin/shop/categories_create.html",{
            'formbundle':[
            ("Category details",form),]
        })

class CategoriesEdit(View):
    def get(self, request, *args, **kwargs):
        try:
            category = shop_models.ProductCategories.objects.get(pk=kwargs.pop("category_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No category matches the given query.")
        form = shop_forms.ProductCategoryForm(instance = category)
        return  render(request, "admin/shop/categories_edit.html",{
            'formbundle':[
            ("Category details",form),]
        })
    def post(self, request, *args, **kwargs):
        try:
            category = shop_models.ProductCategories.objects.get(pk=kwargs.pop("category_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No category matches the given query.")
        form = shop_forms.ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_data = form.save(commit=False) #Modelform
            category_data.parent_slug =  category_data.parent.slug
            category_data.save()

            messages.success(request, 'Save successful..')
            return shortcuts.redirect("admin_shop_categories")
        else:
            messages.error(request, 'category not saved..')
        return  render(request, "admin/shop/categories_edit.html",{
            'formbundle':[
            ("Category details",form),]
        })

class CategoriesDelete(View):
    def get(self, request, *args, **kwargs):
        try:
            category = shop_models.ProductCategories.objects.get(pk=kwargs.pop("category_id"))
        except shop_models.Product.DoesNotExist:
            raise http.Http404("No category matches the given query.")
        try:
            category.delete()
        except:
            return http.JsonResponse({'status': 'failed'})
        return http.JsonResponse({'status': 'success'})


class VendorAdmin(View):
    def get(self, request, *args, **kwargs):
        table = dict()
        table['headers'] = ["Name", "Code", "User","Actions"]
        table['fields'] = ["name", "code", "user", "admin/shop/vendor_table_actions.html"]
        items_list = shop_models.Vendors.objects.all()
        page_no = request.GET.get('page')
        page_size = 10
        table["data"] = helpers.paginate(items_list,page_no,page_size)

        return  render(request, "admin/shop/vendors.html",{
        'table':table,
        })

class VendorsCreate(View):
    def get(self, request, *args, **kwargs):
        form = shop_forms.VendorForm()
        vendor_address_form = shop_forms.AddressForm()
        return  render(request, "admin/shop/categories_create.html",{
            'formbundle':[
            ("Vendor details",form),
            ("Vendor address",vendor_address_form),]
        })

    def post(self, request, *args, **kwargs):
        form = shop_forms.VendorForm(request.POST)
        address_form = shop_forms.AddressForm(request.POST)
        if form.is_valid() and address_form.is_valid():
            vendor = form.save()
            addr = address_form.save()

            vendor_address = shop_models.VendorAddress(vendor=vendor,addr=addr)
            vendor_address.save()

            messages.success(request, 'Save successful..')
            return shortcuts.redirect("admin_shop_vendors")
        else:
            messages.error(request, 'Vendor not saved..')
        return  render(request, "admin/shop/vendors_create.html",{
            'formbundle':[
            ("Vendor details",form),
            ("Vendor address",vendor_address_form),]
        })

class VendorsEdit(View):
    def get(self, request, *args, **kwargs):
        try:
            vendor = shop_models.Vendors.objects.get(pk=kwargs.pop("vendor_id"))
            vendor_address = shop_models.VendorAddress.objects.filter(vendor=vendor).first()
        except shop_models.Vendors.DoesNotExist:
            raise http.Http404("No 'vendor' matches the given query.")
        form = shop_forms.VendorForm(instance = vendor)
        vendor_address_form = shop_forms.AddressForm(instance = vendor_address.addr)
        return  render(request, "admin/shop/vendors_edit.html",{
            'formbundle':[
            ("Vendor details",form),
            ("Vendor address",vendor_address_form),]
        })
    def post(self, request, *args, **kwargs):
        try:
            vendor = shop_models.Vendors.objects.get(pk=kwargs.pop("vendor_id"))
            vendor_address = shop_models.VendorAddress.objects.filter(vendor=vendor).first()
        except shop_models.Vendors.DoesNotExist:
            raise http.Http404("No 'vendor' matches the given query.")
        form = shop_forms.VendorForm(request.POST, instance = vendor)
        address_form = shop_forms.AddressForm(request.POST, instance = vendor_address.addr)
        if form.is_valid() and address_form.is_valid():
            vendor = form.save()
            addr = address_form.save()
            messages.success(request, 'Save successful..')
            return shortcuts.redirect("admin_shop_vendors")
        else:
            messages.error(request, 'Vendor not saved..')
        return  render(request, "admin/shop/vendors_edit.html",{
            'formbundle':[
            ("Vendor details",form),
            ("Vendor address",vendor_address_form),]
        })

class VendorsDelete(View):
    def get(self, request, *args, **kwargs):
        try:
            vendor = shop_models.Vendors.objects.get(pk=kwargs.pop("vendor_id"))
            vendor_address = shop_models.VendorAddress.objects.filter(vendor=vendor).first()
        except shop_models.Vendors.DoesNotExist:
            raise http.Http404("No vendor matches the given query.")
        try:
            vendor_address.addr.delete()
            vendor_address.delete()
            vendor.delete()
        except:
            return http.JsonResponse({'status': 'failed'})
        return http.JsonResponse({'status': 'success'})
