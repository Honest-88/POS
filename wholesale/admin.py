from django.contrib import admin
from django.forms import inlineformset_factory, BaseModelForm
from django.forms import BaseModelFormSet, formset_factory
from django.forms.models import BaseInlineFormSet
from .models import Transaction, Product, Customer, TransactionProduct
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.html import mark_safe
from django.db.models import Sum
from django.contrib.admin.views.main import ChangeList
from itertools import chain


@admin.register(TransactionProduct)
class TransactionProductAdmin(admin.ModelAdmin):
    pass

class TransactionProductForm(forms.ModelForm):
    class Meta:
        model = TransactionProduct
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'admin-product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'admin-product-quantity'}),
        }

TransactionProductFormSet = forms.inlineformset_factory(
    Transaction,
    TransactionProduct,
    form=TransactionProductForm,
    extra=1,
    can_delete=True,
)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['product', 'quantity', 'cost_per_case']
        widgets = {
            'product': forms.Select(attrs={'class': 'admin-autocomplete'}),
        }

TransactionInlineFormSet = forms.inlineformset_factory(Customer, Transaction, form=TransactionForm, extra=1, min_num=1, validate_min=True)


class ProductInline(admin.TabularInline):
    model = Transaction.product.through
    extra = 1
   

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_case', 'grand_total_cases', 'grand_total_amount']
    list_filter = ['name']
    search_fields = ['product', 'customer__name']

    inlines = [ProductInline]

    def grand_total_cases(self, obj):
        total_cases = TransactionProduct.objects.aggregate(grand_total_cases=Sum('quantity'))['grand_total_cases']
        return total_cases or 0

    def grand_total_amount(self, obj):
        return TransactionProduct.objects.aggregate(total_amount=Sum('total_amount_owed'))['total_amount']

class TransactionInline(admin.TabularInline):
    model = Transaction
    formset = TransactionInlineFormSet
    extra = 1

class TransactionProductInlineFormSet(BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['transaction'] = self.instance
        return kwargs

class TransactionProductInline(admin.TabularInline):
    model = TransactionProduct
    formset = TransactionProductInlineFormSet
    extra = 1
    
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        fields.remove('cost_per_case')
        return fields
    


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [TransactionInline]
    list_display = ['name',]
    list_filter = ["name"]
    search_fields = ['name', 'customer__name', 'transactions__product__name']

    inlines = [TransactionInline]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [TransactionInline]
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            formset.instance.total_cases = sum([form.cleaned_data['quantity'] for form in formset.forms])
            formset.instance.total_amount_owed = sum([form.cleaned_data['quantity'] * form.cleaned_data['cost_per_case'] for form in formset.forms])
            formset.instance.save()


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    inlines = [TransactionProductInline]
    list_display = ('customer', 'get_product_list', 'get_total_amount_owed', 'get_total_cases',
     'grand_total_cases', 'grand_total_amount', 'date', 'week_of',)
    readonly_fields = ('total_amount_owed', 'get_total_amount_owed', 'get_total_cases', 'total_cases')
    list_filter = ['customer', 'date']
    search_fields = ['product', 'customer', 'date']
    date_hierarchy = 'date'

    list_per_page = 10  # Number of items to display per page
    list_max_show_all = 100  # Maximum number of items to display when "Show all" is clicked

    
    fieldsets = (
        (None, {
            'fields': ('customer', 'date'),
        }),
        ('Transaction Details', {
            'fields': (('product', 'quantity', 'cost_per_case'),),
            'classes': ('collapse',),
        }),
    )

    
#========================================================================================================

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [TransactionProductInline]
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        transaction = form.instance
        transaction.total_cases = sum(tp.quantity for tp in transaction.transactionproduct_set.all())
        transaction.total_amount_owed = sum(tp.quantity * tp.cost_per_case for tp in transaction.transactionproduct_set.all())
        transaction.save()

    def get_product_list(self, obj):
        product = obj.product.all()
        return ', '.join([str(product) for product in obj.product.all()])

    get_product_list.short_description = 'Product List'


    def get_product_list(self, obj):
        transaction_products = obj.transactionproduct_set.all()
        table_html = '<table style="border-collapse: collapse;">'
        table_html += '<tr><th>Product Name</th><th>Quantity</th><th>Cost per Case</th><th>Total Amount Owed</th></tr>'
        
        for transaction_product in transaction_products:
            table_html += '<tr>'
            table_html += f'<td style="border: 1px solid black;">{transaction_product.product.name}</td>'
            table_html += f'<td style="border: 1px solid black;">{transaction_product.quantity}</td>'
            table_html += f'<td style="border: 1px solid black;">{transaction_product.cost_per_case}</td>'
            table_html += f'<td style="border: 1px solid black;">{transaction_product.total_amount_owed}</td>'
            table_html += '</tr>'
        
        table_html += '</table>'
        
        return mark_safe(table_html)


    get_product_list.short_description = 'Product Details'


    fieldsets = (
        ('Transaction Details', {
            'fields': ('customer', 'date'),
        }),
    )
    

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = [ProductInline]
        return super().add_view(request, form_url, extra_context=extra_context)

  
    def save_model(self, request, obj, form, change, formsets=None):
        super().save_model(request, obj, form, change)
        if formsets is not None:
            obj.total_cases = sum([form.cleaned_data['quantity'] for form in formsets[0].forms])
            obj.total_amount_owed = sum([form.cleaned_data['quantity'] * form.cleaned_data['cost_per_case'] for form in formsets[0].forms])
            obj.save()
        

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('customer')
        return queryset

    def get_product_quantity(self, obj):
        return obj.quantity

    get_product_quantity.short_description = 'Quantity'

    def get_cost_per_case(self, obj):
        return obj.cost_per_case

    get_cost_per_case.short_description = 'Cost per Case'

    def get_total_amount_owed(self, obj):
        transaction_products = obj.transactionproduct_set.all()
        total_amount = sum([transaction_product.quantity * transaction_product.cost_per_case for transaction_product in transaction_products])
        return total_amount

    get_total_amount_owed.short_description = 'Overall Amount Owed'


    def get_total_cases(self, obj):
        transaction_products = obj.transactionproduct_set.all()
        total_cases = sum([transaction_product.quantity for transaction_product in transaction_products])
        return total_cases
    
    get_total_cases.short_description = 'Total Cases'

    def grand_total_amount(self, obj):
        total_amount = TransactionProduct.objects.aggregate(grand_total_amount=Sum('total_amount_owed'))['grand_total_amount']
        return total_amount or 0
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(total_amount=Sum('transactionproduct__total_amount_owed'))
        return queryset

    grand_total_amount.short_description = 'Grand Total Amount'


    def grand_total_cases(self, obj):
        total_cases = TransactionProduct.objects.aggregate(grand_total_cases=Sum('quantity'))['grand_total_cases']
        return total_cases or 0

    grand_total_cases.short_description = 'Grand Total Cases'


    def total_amount_owed(self, obj):
        return obj.transactionproduct_set.aggregate(total_amount=Sum('total_amount_owed'))['total_amount']
    
    def total_cases(self, obj):
        return obj.transactionproduct_set.aggregate(total_cases=Sum('quantity'))['total_cases']



    def customer_name(self, obj):
        return obj.customer.name

    def product_name(self, obj):
        return obj.product.name

  
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, TransactionProductInline):
                formset = TransactionProductFormSet
            else:
                formset = inline.get_formset(request, obj)
            yield formset, inline

    #==================================================================================================

#================================================================================================================











