# Generated by Django 4.1.5 on 2023-06-12 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wholesale', '0008_remove_transaction_product_transactionproduct_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionproduct',
            name='cost_per_case',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
