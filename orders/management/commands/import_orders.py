import logging
import xml.etree.ElementTree as ET

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator

from orders.models import Order
from utils.utils import AbstractImporter, URLFetcher

logger = logging.getLogger("command_logger")


class OrderImporter(AbstractImporter):
    """Responsible for parsing XML content and importing order data into the database."""

    def parse_and_save(self, xml_content: bytes) -> int:
        """Parses the given XML content and saves order data into the database.

        Args:
            xml_content (bytes): Raw XML content containing order data.

        Returns:
            int: Number of newly created orders.
        """
        root = ET.fromstring(xml_content)
        orders: list = root.findall(".//order")
        if not orders:
            return 0

        imported_count = 0
        for order_elem in orders:
            order_id = order_elem.findtext("order_id", default="").strip()
            marketplace = order_elem.findtext("marketplace", default="").strip()
            amount = order_elem.findtext("order_amount", default="0").strip()
            currency = order_elem.findtext("order_currency", default="").strip()
            address = order_elem.findtext(
                ".//delivery_full_address", default=""
            ).strip()

            if not order_id:
                logger.warning("Order skipped: missing order_id.")
                continue

            if not address or "None" in address:
                address = "Address not available"

            _, created = Order.objects.update_or_create(
                order_id=order_id,
                defaults={
                    "marketplace": marketplace,
                    "order_amount": amount,
                    "order_currency": currency,
                    "delivery_full_address": address,
                },
            )
            imported_count += 1 if created else 0

        return imported_count


class Command(BaseCommand):
    help = "Import orders from an XML file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            help="(Optional) Override the default URL of the XML file",
        )

    def handle(self, *args, **kwargs):
        url = kwargs.get("url") or getattr(settings, "DEFAULT_ORDER_URL", "")
        try:
            URLValidator()(url)
        except ValidationError:
            raise CommandError(
                "A valid URL must be provided via --url or in settings.DEFAULT_ORDER_URL."
            )

        fetcher = URLFetcher()
        importer = OrderImporter()

        try:
            content = fetcher.fetch(url)
        except requests.HTTPError as e:
            raise CommandError(
                f"HTTP Error while fetching content : {e.response.status_code}"
            )
        except requests.RequestException as e:
            raise CommandError(f"Network error while fetching: {e}")

        try:
            count = importer.parse_and_save(content)
            if count == 0:
                self.stdout.write(self.style.WARNING("No new orders imported."))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} new order(s).")
                )
        except ET.ParseError as e:
            logger.error("Invalid XML format", exc_info=e)
            raise CommandError(f"Invalid XML format : {e}")
        except Exception as e:
            logger.error("Unexpected error while processing XML", exc_info=e)
            raise CommandError(f"Unexpected error while processing XML : {e}")
