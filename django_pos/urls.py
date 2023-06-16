
from django.contrib import admin
from django.urls import include, path
from django.urls import include, re_path
from django.views.static import serve
from django.conf import settings
from billmanage import views as billviews  

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication: Login and Logout
    path('', include('authentication.urls')),
    # Index
    path('', include('pos.urls')),
    # Products
    path('products/', include('products.urls')),
    # Customers
    path('customers/', include('customers.urls')),
    # Sales
    path('sales/', include('sales.urls')),

    path('billmanage/', include('billmanage.urls')),

    path('wholesale/', include('wholesale.urls')),

    #billmanage urls
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root':       settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]
