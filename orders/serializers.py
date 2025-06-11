from rest_framework import serializers

from orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model"""

    class Meta:
        model = Order
        fields = [
            "id",
            "order_id",
            "marketplace",
            "order_amount",
            "order_currency",
            "delivery_full_address",
        ]
