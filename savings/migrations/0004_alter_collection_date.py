# Generated by Django 5.1.3 on 2024-12-21 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0003_remove_worker_assigned_customers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
