from django.contrib import admin
from .models import bill, item
# Register your models here.
class billadmin(admin.ModelAdmin):
    list_display = ('invoice_type', 'billno', 'recipient', 'date', 'address', 'delivery', 'GSTno', 'cgst', 'sgst', 'total', 'grandtotal')
admin.site.register(bill, billadmin)

class itemadmin(admin.ModelAdmin):
    list_display = ('itemno','billno', 'itemname', 'hsncode', 'qty', 'rate', 'amount')

admin.site.register(item, itemadmin)