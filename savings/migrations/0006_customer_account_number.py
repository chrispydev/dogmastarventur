# Generated by Django 5.1.3 on 2024-12-26 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0005_customer_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='account_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
