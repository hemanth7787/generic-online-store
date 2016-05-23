from django.conf.urls import include, url, patterns
from django.conf import settings

urlpatterns = [
    url(r'^admin/shop/', include('shop.admin_urls')),
    url(r'^shop/', include('shop.urls')),
    url(r'^auth/', include('user_profiles.urls')),
    url(r'^order/', include('order.urls')),
    url(r'^', include('gs_core.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
