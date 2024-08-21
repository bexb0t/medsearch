import logging

from typing import Dict, List, Optional
from lxml import etree

from medsearch_api.app.dailymed_response.base_dailymed_response import (
    BaseDailyMedResponse,
)
from medsearch_api.app.xml.utils import XMLLocation

logger = logging.getLogger(__name__)


class SPLListItemResponse(BaseDailyMedResponse):
    """Represents a single SPL (Structured Product Label) entry."""

    # Define attributes for each SPL entry
    set_id: str
    spl_version: str
    title: str
    published_date: str

    # Specify the XML locations for these attributes
    xml_fields: Dict[str, XMLLocation] = {
        "set_id": XMLLocation(xpath="setid", attrib=None),
        "spl_version": XMLLocation(xpath="spl_version", attrib=None),
        "title": XMLLocation(xpath="title", attrib=None),
        "published_date": XMLLocation(xpath="published_date", attrib=None),
    }

    def __init__(self, raw_xml_response: bytes):
        super().__init__(raw_xml_response)
        self.initialize_fields()

    def log_xml_parsing_issue(self, error: ValueError):
        """Logs XML parsing issues encountered for this SPL item.

        Args:
            error (ValueError): The error encountered during XML parsing.
        """
        error_message = str(error)
        logger.error(f"Error parsing XML for SPLItem: {error_message}")


class SPLListResponse(BaseDailyMedResponse):
    """Represents a response containing a list of SPL (Structured Product Label) entries."""

    # Define the attributes we are tracking
    total_elements: int
    elements_per_page: int
    total_pages: int
    current_page: int
    current_url: int
    previous_page: Optional[int] = None
    previous_page_url: Optional[str] = None
    next_page: Optional[int] = None
    next_page_url: Optional[str] = None

    # Specify the locations of these attributes
    xml_fields: Dict[str, XMLLocation] = {
        "total_elements": XMLLocation(xpath="metadata/total_elements", attrib=None),
        "elements_per_page": XMLLocation(
            xpath="metadata/elements_per_page", attrib=None
        ),
        "total_pages": XMLLocation(xpath="metadata/total_pages", attrib=None),
        "current_page": XMLLocation(xpath="metadata/current_page", attrib=None),
        "current_url": XMLLocation(xpath="metadata/current_url", attrib=None),
        "previous_page": XMLLocation(xpath="metadata/previous_page", attrib=None),
        "previous_page_url": XMLLocation(
            xpath="metadata/previous_page_url", attrib=None
        ),
        "next_page": XMLLocation(xpath="metadata/next_page", attrib=None),
        "next_page_url": XMLLocation(xpath="metadata/next_page_url", attrib=None),
    }

    def __init__(self, raw_xml_response: bytes):
        super().__init__(raw_xml_response)
        # Initialize metadata attributes
        self.initialize_fields()
        self.spl_list_items = self.parse_spl_entries()

    def log_xml_parsing_issue(self, error: ValueError):
        #  TODO: Implement logging or handling of XML parsing issues
        print(f"XML Parsing Issue: {error}")

    def parse_spl_entries(self) -> List[SPLListItemResponse]:
        """Parses SPL entries from the XML response.

        Returns:
            List[SPLListItemResponse]: A list of SPLListItemResponse instances representing the SPL entries.
        """
        return [
            SPLListItemResponse(etree.tostring(spl_element))
            for spl_element in self.document.findall(".//spl")
        ]

    @property
    def has_more_pages(self) -> bool:
        """Checks if there are more pages of results available.

        Returns:
            bool: True if there are more pages, False otherwise.
        """
        return bool(self.total_pages and self.current_page < self.total_pages)
