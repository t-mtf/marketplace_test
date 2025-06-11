from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.test import TestCase

from orders.models import Order


class OrderModelTest(TestCase):
    """Test cases for the Order model"""

    def setUp(self):
        self.order = Order.objects.create(
            order_id="123ABC",
            marketplace="Amazon",
            order_amount=Decimal("12.34"),
            order_currency="EUR",
            delivery_full_address="1 Rue Dupont 44000 Nantes FR",
        )

    def test_order_creation(self):
        """Test that an order can be created"""
        self.assertEqual(self.order.order_id, "123ABC")
        self.assertEqual(self.order.marketplace, "Amazon")
        self.assertEqual(self.order.order_amount, Decimal("12.34"))
        self.assertEqual(self.order.order_currency, "EUR")
        self.assertEqual(
            self.order.delivery_full_address, "1 Rue Dupont 44000 Nantes FR"
        )

    def test_order_unique_constraint(self):
        """Test the unicity constraint on order_id"""
        with pytest.raises(IntegrityError):
            Order.objects.create(
                order_id=self.order.order_id,
                marketplace=self.order.marketplace,
                order_amount=self.order.order_amount,
                order_currency=self.order.order_currency,
                delivery_full_address=self.order.delivery_full_address,
            )

    def test_order_string_representation(self):
        """Test the string representation of an order"""
        self.assertEqual(str(self.order), "123ABC - Amazon - 12.34EUR")
