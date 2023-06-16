from .views import customer_list, add_transaction, total_amount_owed, product_list, add_product, add_customer
from django.urls import include, path
from django.views.static import serve
from wholesale import views as views  
from django.urls import reverse

app_name = "wholesale"
    #wholesale urls

urlpatterns = [
    path('add-customer/', views.add_customer, name='add_customer'),
    path('customer-list/', views.customer_list, name='customer_list'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('add-transaction/<int:customer_id>/', views.add_transaction, name='add_transaction_with_id'),
    path('total-amount-owed/', total_amount_owed, name='total_amount_owed'),
    path('add-product/', add_product, name='add_product'),
    path('product-list/', product_list, name='product_list'),

    # Add other URLs as needed
]
