# Generated by Django 4.1.5 on 2023-01-13 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_product_price"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"verbose_name_plural": "Categories"},
        ),
        migrations.AlterField(
            model_name="product",
            name="status",
            field=models.CharField(
                choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive")],
                max_length=100,
                verbose_name="Status of the product",
            ),
        ),
    ]