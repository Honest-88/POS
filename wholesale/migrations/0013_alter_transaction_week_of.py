# Generated by Django 4.1.5 on 2023-06-12 20:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wholesale', '0012_transaction_week_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='week_of',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
