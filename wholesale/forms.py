from django import forms
from .models import Transaction, Customer, Product


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['customer', 'product', 'quantity']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price_per_case']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_case': forms.NumberInput(attrs={'class': 'form-control'}),
        }



class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name',]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
           # 'address': forms.TextInput(attrs={'class': 'form-control'}),
        }