from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Transaction, Product
from .forms import TransactionForm, CustomerForm, ProductForm
from django.db.models import F, Sum


def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wholesale:add_customer')
    else:
        form = CustomerForm()
    
    return render(request, 'wholesale/add_customer.html', {'form': form})


def customer_list(request):
    customers = Customer.objects.annotate(
        total_cases=Sum('transaction__quantity'),
        total_price=Sum(F('transaction__quantity') * F('transaction__product__price_per_case'))
    ).prefetch_related('transaction_set__product')
    
    transactions = Transaction.objects.select_related('customer', 'product').all()

    return render(request, 'wholesale/customer_list.html', {'customers': customers, 'transactions': transactions})



def add_transaction(request, customer_id=None):
    customer = get_object_or_404(Customer, id=customer_id) if customer_id else None
    customers = Customer.objects.all()  # Retrieve all customers
    products = Product.objects.all()
    transactions = Transaction.objects.filter(customer=customer) if customer else Transaction.objects.all()

    total_amount_owed = transactions.aggregate(total_amount=Sum('total_amount_owed')).get('total_amount')
    total_cases = transactions.aggregate(total_cases=Sum('quantity')).get('total_cases')

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.customer = form.cleaned_data['customer']
            transaction.product = form.cleaned_data['product']
            transaction.save()

            # Update the customer's transaction details
            customer = transaction.customer
            customer.products.add(transaction.product)
            customer.add_transaction(transaction.product, transaction.quantity)

            customer = form.cleaned_data['customer']
            # Process the product quantities
            for product in products:
                quantity = int(request.POST.get(f'quantity_{product.id}', 0))
                if quantity > 0:
                    # Create a transaction for the product and customer
                    transaction = Transaction.objects.create(customer=customer, product=product, quantity=quantity)
                    customer.products.add(product)
                    customer.add_transaction(product, quantity)

            return redirect('wholesale:add_transaction')
    else:
        form = TransactionForm()

    # Calculate grand total cases and grand total amount
    grand_total_cases = Transaction.objects.aggregate(total_cases=Sum('quantity')).get('total_cases')
    grand_total_amount = Transaction.objects.aggregate(total_amount=Sum('total_amount_owed')).get('total_amount')

    if customer:
        total_price = customer.transactions.aggregate(total_price=Sum('total_amount_owed')).get('total_price')
        if total_price is None:
            total_price = 0

        context = {
            'customer': customer,
            'total_price': total_price,
        }
    else:
        context = {
            'form': form,
            'transactions': transactions,
            'customer': customer,
            'total_amount_owed': total_amount_owed,
            'grand_total_cases': grand_total_cases,
            'grand_total_amount': grand_total_amount,
            'products': products,
            'customers': customers,  # Include the customers queryset in the
            # Other context variables...
        }

    return render(request, 'wholesale/add_transaction.html', context)

def total_amount_owed(request):
    customers = Customer.objects.annotate(total_amount=Sum('transaction__quantity' * 'transaction__product__price_per_case'))

    return render(request, 'total_amount_owed.html', {'customers': customers})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wholesale:add_product')
    else:
        form = ProductForm()
    return render(request, 'wholesale/add_product.html', {'form': form})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'wholesale/product_list.html', {'products': products})


def calculate_grand_total_amount():
    transactions = Transaction.objects.all()
    grand_total_amount = sum(transaction.customer.total_amount_owed for transaction in transactions)
    return grand_total_amount


def calculate_grand_total_cases():
    transactions = Transaction.objects.all()
    grand_total_cases = sum(transaction.customer.total_cases for transaction in transactions)
    return grand_total_cases
