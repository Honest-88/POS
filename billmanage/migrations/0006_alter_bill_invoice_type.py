# Generated by Django 4.1.5 on 2023-06-01 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billmanage', '0005_alter_bill_invoice_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='invoice_type',
            field=models.CharField(choices=[('quotation', 'Quotation'), ('proforma', 'Proforma Invoice'), ('sales', 'Sales Invoice')], default='Quotation', max_length=20),
        ),
    ]