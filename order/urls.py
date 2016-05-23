from django.conf.urls import patterns, url
from order import views as order_views

urlpatterns = patterns('',
    url(r'^checkout_summary/(?P<order_id>\d+)/$', order_views.CheckoutSummary.as_view(), name='order_checkout_summary'),
)
