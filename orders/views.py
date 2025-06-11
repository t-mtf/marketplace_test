from rest_framework import generics

from orders.models import Order
from orders.serializers import OrderSerializer


class OrderListView(generics.ListAPIView):
    """API view to list all orders"""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderDetailView(generics.RetrieveAPIView):
    """API view to retrieve a specific order"""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
