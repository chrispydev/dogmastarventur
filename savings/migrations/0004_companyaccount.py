# Generated by Django 5.1.3 on 2025-03-10 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0003_alter_customer_account_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
            ],
        ),
    ]
