from django.db import models
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField('Product', related_name='customers')

    # Add other customer details as needed

    class Meta:
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name

    def get_total_cases(self):
        return sum([product.quantity for product in self.products.all()])


    # def calculate_total_cases(self):
       #return self.transactions.aggregate(total_cases=Sum('quantity'))['total_cases']
            

    def add_transaction(self, product, quantity, date):
        transaction = Transaction.objects.create(customer=self, product=product, quantity=quantity, date=date)
        self.save()


class Product(models.Model):
    name = models.CharField(max_length=100)
    price_per_case = models.DecimalField(max_digits=8, decimal_places=2)
    # Add other product details as needed

    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name


class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, through='TransactionProduct')
    quantity = models.PositiveIntegerField(default=0)
    cost_per_case = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_amount_owed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_cases = models.IntegerField(blank=True, null=True)
    date = models.DateField(default=timezone.now) 
    week_of = models.DateField(default=timezone.now)


    # Add other transaction details as needed
    class Meta:
        verbose_name_plural = "Transactions"


    def get_total_cases(self):
        return self.quantity


    def get_total_amount_owed(self):
            transaction_products = self.transactionproduct_set.all()
            total_amount = sum([transaction_product.quantity * transaction_product.cost_per_case for transaction_product in transaction_products])
            return total_amount

    def save(self, *args, **kwargs):
        self.total_amount_owed = self.quantity * self.cost_per_case
        super().save(*args, **kwargs)

    
    def save(self, *args, **kwargs):
        self.total_amount_owed = self.quantity * self.cost_per_case
        self.total_cases = self.quantity
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Transaction ID: {self.id}, Customer: {self.customer.name}, Product: {self.product.name}, Quantity: {self.quantity}, Date: {self.date}"


class TransactionProduct(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    cost_per_case = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    total_amount_owed = models.DecimalField(default=0, max_digits=8, decimal_places=2)


    class Meta:
        verbose_name_plural = 'Transaction Products'

   
    def get_total_amount_owed(self):
        transaction_products = self.transactionproduct_set.all()
        total_amount = sum([transaction_product.quantity * transaction_product.cost_per_case for transaction_product in transaction_products])
        return total_amount

    def save(self, *args, **kwargs):
        self.total_amount_owed = self.quantity * self.cost_per_case
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.transaction} - {self.product} - Quantity: {self.quantity}'


 
   
  






