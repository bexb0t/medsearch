import logging
from datetime import date

import requests
from urllib.parse import urljoin
from typing import Optional

logger = logging.getLogger(__name__)


class DailyMedClient:
    """Client for interacting with the DailyMed API.

    Attributes:
        BASE_URL (str): The base URL for the DailyMed API.
    """

    BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2/"

    @staticmethod
    def format_date(date: date) -> str:
        """Formats a date as a string in the format YYYY-MM-DD.

        Args:
            date (date): The date to be formatted.

        Returns:
            str: The formatted date string.
        """
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def construct_url(endpoint: str, **params) -> str:
        """Constructs the full URL for the API request.

        Args:
            endpoint (str): The API endpoint to append to the base URL.
            **params: Additional query parameters to include in the URL.

        Returns:
            str: The constructed URL with query parameters.
        """
        url = urljoin(DailyMedClient.BASE_URL, endpoint)
        if params:
            url += "?" + "&".join(f"{key}={value}" for key, value in params.items())
        return url

    def fetch(self, endpoint: str, **params) -> Optional[bytes]:
        """
        Fetches data from the DailyMed API at the specified endpoint.

        Args:
            endpoint (str): The specific endpoint to be accessed.
            **params: Additional query parameters.

        Returns:
            Optional[bytes]: The raw content of the response if successful; otherwise, None.
        """
        url = self.construct_url(endpoint, **params)
        logger.debug(f"Fetching data from API at {url}")
        response = requests.get(url)

        if response.status_code == 200:
            logger.debug(f"Successful response from {url}")
            return response.content
        else:
            logger.error(
                f"Failed to fetch data from {url}, status code: {response.status_code}"
            )
            return None

    def fetch_spls(
        self, page_number: int, published_after: Optional[date] = None
    ) -> Optional[bytes]:
        """Fetches SPL data from DailyMed API.

        Args:
            page_number (int): The page number to fetch.
            published_after (Optional[date]): Optional date to filter SPLs published after this date.

        Returns:
            Optional[bytes]: The raw content of the response if the request is successful; otherwise, None.
        """
        endpoint = "spls.xml"
        if published_after:
            formatted_date = self.format_date(published_after)
            endpoint += f"?published_date={formatted_date}&published_date_comparison=gt"
        endpoint += f"&page={page_number}"

        return self.fetch(endpoint)

    def fetch_spl_by_set_id(self, set_id: str) -> Optional[bytes]:
        """
        Fetches a specific SPL by its set_id.

        Args:
            set_id (str): The ID of the SPL to fetch.

        Returns:
            Optional[bytes]: The raw content of the response if successful; otherwise, None.
        """
        return self.fetch(f"spls/{set_id}")
