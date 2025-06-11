from django.db import models


class Order(models.Model):
    """Model representing an order from the marketplace"""

    order_id = models.CharField(unique=True)
    marketplace = models.CharField(max_length=100)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_currency = models.CharField(max_length=3)
    delivery_full_address = models.TextField()

    def __str__(self):
        return f"{self.order_id} - {self.marketplace} - {self.order_amount}{self.order_currency}"
