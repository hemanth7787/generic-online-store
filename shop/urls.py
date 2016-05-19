from django.conf.urls import patterns, url
from shop import views as shop_views

urlpatterns = patterns('',
    url(r'^products/$', shop_views.ProductsList.as_view(), name='shop_products_list'),
    url(r'^products/(?P<product_id>\d+)/details/$', shop_views.ProductDetails.as_view(), name='shop_products_details'),
    url(r'^basket/add/$', shop_views.BasketAddItem.as_view(), name='shop_basket_add'),
    url(r'^basket/modify/$', shop_views.BasketModifyItem.as_view(), name='shop_basket_modify'),
    url(r'^basket/list/$', shop_views.BasketListItems.as_view(), name='shop_basket_list'),
    url(r'^checkout/$', shop_views.Checkout.as_view(), name='shop_checkout'),
    url(r'^checkout_summary/$', shop_views.CheckoutSummary.as_view(), name='shop_checkout_summary'),
)
