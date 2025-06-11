import logging
import requests
from abc import ABC, abstractmethod
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_fixed,
)
from dataclasses import dataclass

logger = logging.getLogger("utils_logger")


class AbstractImporter(ABC):
    @abstractmethod
    def parse_and_save(self, xml_content: bytes) -> int:
        pass


@dataclass
class URLFetcher:
    """A utility class responsible for fetching the content of a given URL"""

    retries: int = 5
    wait: int = 3

    def should_retry(self, exception) -> bool:
        """Determines whether an exception justifies a retry

        Args:
            exception (Exception): The exception to evaluate

        Returns:
            bool: True if a retry attempt is recommended, False otherwise
        """
        if isinstance(exception, (requests.ConnectionError, requests.Timeout)):
            return True
        if isinstance(exception, requests.HTTPError):
            if exception.response and 500 <= exception.response.status_code < 600:
                return True
        return False

    def fetch(self, url: str) -> bytes:
        """Download the raw content (in bytes) from given url.

        Args:
            url (str): The url of the file to download

        Returns:
            bytes: The raw response content
        """

        @retry(
            stop=stop_after_attempt(self.retries),
            wait=wait_fixed(self.wait),
            retry=retry_if_exception(self.should_retry),
        )
        def _get():
            response = requests.get(url)
            response.raise_for_status()
            return response.content

        try:
            logger.info("Fetching xml content")
            return _get()
        except requests.HTTPError as e:
            logger.error(
                f"HTTP error for {url}: {e} - Status: {e.response.status_code}"
            )
            raise
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning(f"Network error for {url}: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request exception for {url}: {e}")
            raise
