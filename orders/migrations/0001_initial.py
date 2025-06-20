# Generated by Django 5.2.3 on 2025-06-11 08:48

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order_id", models.CharField(unique=True)),
                ("marketplace", models.CharField(max_length=100)),
                ("order_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("order_currency", models.CharField(max_length=3)),
                ("delivery_full_address", models.TextField()),
            ],
        ),
    ]
