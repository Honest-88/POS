from django.urls import path
from . import views
from django.urls import include, re_path
from django.views.static import serve
from billmanage import views as billviews  


app_name = "billmanage"
urlpatterns = [
    #billmanage urls
    path('', billviews.loginview, name='login'),
    path('dashboard/', billviews.dashboard, name='dashboard'),
    path('addbill', billviews.addbill, name='addbill'),
    path('records', billviews.records, name='records'),
    path('invoice/<int:billno>', billviews.invoice, name='invoice'),
    path('delete/<int:billno>', billviews.delete, name='delete'),
    path('addbill_submitted', billviews.addbill_submitted, name='addbill_submitted'),

    
]
