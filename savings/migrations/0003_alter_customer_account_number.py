# Generated by Django 5.1.3 on 2025-01-25 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0002_customer_account_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='account_number',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
