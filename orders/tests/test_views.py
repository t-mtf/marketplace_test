from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order


class OrderAPITest(APITestCase):
    """Test cases for the Order API views"""

    def setUp(self):
        self.order_1 = Order.objects.create(
            order_id="123ABC",
            marketplace="Amazon",
            order_amount=Decimal("12.34"),
            order_currency="EUR",
            delivery_full_address="1 Rue Dupont 44000 Nantes FR",
        )

        self.order_2 = Order.objects.create(
            order_id="456DEF",
            marketplace="Cdiscount",
            order_amount=Decimal("56.78"),
            order_currency="EUR",
            delivery_full_address="2 Rue Jean 44100 Nantes FR",
        )

    def test_list_orders(self):
        """Test retrieving a list of orders"""
        url = reverse("order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_order(self):
        """Test retrieving a specific order by its id"""
        url = reverse("order-detail", args=[self.order_2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("order_id"), "456DEF")
        self.assertEqual(response.data.get("marketplace"), "Cdiscount")

    def test_order_not_found(self):
        """Test retrieving not existing order"""
        url = reverse("order-detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
