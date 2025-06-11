from decimal import Decimal
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from requests import HTTPError, Timeout
from tenacity import RetryError

from orders.management.commands.import_orders import OrderImporter, URLFetcher
from orders.models import Order

VALID_XML = b"""
<root>
    <orders>
        <order>
            <order_id>123ABC</order_id>
            <marketplace>Amazon</marketplace>
            <order_amount>12.34</order_amount>
            <order_currency>EUR</order_currency>
            <delivery_full_address>1 Rue Dupont 44000 Nantes FR</delivery_full_address>
        </order>
    </orders>
</root>
"""

INVALID_XML = b"<root><orders><order></root>"


@pytest.mark.django_db
def test_order_import_creates_order():
    importer = OrderImporter()
    count = importer.parse_and_save(VALID_XML)

    assert count == 1
    assert Order.objects.count() == 1
    order = Order.objects.get(order_id="123ABC")
    assert order.marketplace == "Amazon"
    assert order.order_amount == Decimal("12.34")


@pytest.mark.django_db
def test_order_import_skips_missing_order_id():
    xml = b"""
    <root>
        <orders>
            <order>
                <marketplace>Amazon</marketplace>
            </order>
        </orders>
    </root>
    """

    importer = OrderImporter()
    count = importer.parse_and_save(xml)
    assert count == 0
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_order_import_handles_address_none():
    xml = b"""
    <root>
        <orders>
            <order>
                <order_id>345DEF</order_id>
                <marketplace>Amazon</marketplace>
                <order_amount>100</order_amount>
                <order_currency>EUR</order_currency>
                <delivery_full_address>None</delivery_full_address>
            </order>
        </orders>
    </root>
    """
    importer = OrderImporter()
    count = importer.parse_and_save(xml)
    assert count == 1
    assert (
        Order.objects.get(order_id="345DEF").delivery_full_address
        == "Address not available"
    )


def test_url_fetcher_success(monkeypatch):
    def mock_get(*args, **kwargs):
        class Response:
            status_code = 200

            def raise_for_status(self):
                pass

            content = b"<data></data>"

        return Response()

    monkeypatch.setattr("requests.get", mock_get)
    fetcher = URLFetcher()
    result = fetcher.fetch("http://example.com/test.xml")
    assert result == b"<data></data>"


def test_url_fetcher_raises_http_error(monkeypatch):
    def mock_get(*args, **kwargs):
        class Response:
            status_code = 500

            def raise_for_status(self):
                raise HTTPError(response=self)

        return Response()

    monkeypatch.setattr("requests.get", mock_get)
    fetcher = URLFetcher()

    with pytest.raises(RetryError) as exc_info:
        fetcher.fetch("http://example.com/bad.xml")

    assert isinstance(exc_info.value.last_attempt.exception(), HTTPError)


@pytest.mark.django_db
def test_command_success(monkeypatch):
    out = StringIO()

    def mock_fetch(self, url):
        return VALID_XML

    monkeypatch.setattr(
        "orders.management.commands.import_orders.URLFetcher.fetch", mock_fetch
    )

    call_command("import_orders", url="http://fake-url.com", stdout=out)

    assert "Successfully imported 1 new order(s).\n" in out.getvalue()
    assert Order.objects.count() == 1


def test_command_invalid_url():
    with pytest.raises(
        CommandError,
        match="A valid URL must be provided via --url or in settings.DEFAULT_ORDER_URL.",
    ):
        call_command("import_orders", url="invalid-url")


@pytest.mark.django_db
def test_command_invalid_xml(monkeypatch):
    def mock_fetch(self, url):
        return INVALID_XML

    monkeypatch.setattr(
        "orders.management.commands.import_orders.URLFetcher.fetch", mock_fetch
    )

    with pytest.raises(CommandError, match="Invalid XML format"):
        call_command("import_orders", url="http://valid-url.com")


@pytest.mark.django_db
def test_order_import_with_update_or_create_mocked():
    xml = VALID_XML
    importer = OrderImporter()

    with patch("orders.models.Order.objects.update_or_create") as mock_update:
        mock_update.return_value = (MagicMock(), True)  # (instance, created)

        count = importer.parse_and_save(xml)

        assert count == 1
        mock_update.assert_called_once_with(
            order_id="123ABC",
            defaults={
                "marketplace": "Amazon",
                "order_amount": "12.34",
                "order_currency": "EUR",
                "delivery_full_address": "1 Rue Dupont 44000 Nantes FR",
            },
        )


def test_url_fetcher_raises_timeout(monkeypatch):
    def mock_get(*args, **kwargs):
        raise Timeout("Timeout expired")

    monkeypatch.setattr("requests.get", mock_get)
    fetcher = URLFetcher()

    with pytest.raises(RetryError) as exc_info:
        fetcher.fetch("http://example.com/timeout.xml")

    assert isinstance(exc_info.value.last_attempt.exception(), Timeout)
