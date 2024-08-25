import logging
from abc import abstractmethod
from lxml import etree
from typing import Dict, Optional
from medsearch_api.app.xml.utils import XMLLocation, get_xml_value

logger = logging.getLogger(__name__)


class BaseXMLResponse:
    """Base class for parsing NIH DailyMed XML responses.

    Attributes:
        xml_fields (Dict[str, XMLLocation]): A dictionary mapping attribute names to XML locations.
    """

    xml_fields: Dict[str, XMLLocation] = {}

    def __init__(self, raw_xml_response: bytes):
        self.raw_xml_response = raw_xml_response

        parser = etree.XMLParser(
            no_network=True, dtd_validation=False, resolve_entities=False
        )

        self.document = etree.fromstring(self.raw_xml_response, parser)

        self.initialize_fields()

    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if k != "raw_xml_response"}
        return f"{self.__class__.__name__}({attrs})"

    def initialize_fields(self):
        """Initializes the fields defined in xml_fields by parsing the XML response."""

        for attr, xml_location in self.xml_fields.items():
            setattr(self, attr, self.parse_value(xml_location))

    @abstractmethod
    def log_xml_parsing_issue(self, error: ValueError):
        """Logs or handles XML parsing issues.

        This method must be implemented by subclasses.

        Args:
            error (ValueError): The error encountered during XML parsing.
        """
        pass

    def parse_value(self, location: XMLLocation) -> Optional[str]:
        """Parses a value from the XML document based on the given location.

        Args:
            location (XMLLocation): The XML location to extract the value from.

        Returns:
            Optional[str]: The extracted value, or None if parsing fails.
        """
        try:
            return get_xml_value(self.document, location)
        except ValueError as ve:
            self.log_xml_parsing_issue(ve)
            return None

    @staticmethod
    def normalize_tag(tag: str) -> str:
        """Normalizes an XML tag by removing its namespace.

        Args:
            tag (str): The XML tag to normalize.

        Returns:
            str: The normalized tag without namespace.
        """
        return tag.split("}", 1)[-1] if "}" in tag else tag

    @staticmethod
    def get_namespace_prefix(element: etree._Element) -> Optional[str]:
        """Retrieves the namespace prefix of an element.

        Args:
            element: The lxml.etree element.

        Returns:
            Optional[str]: The namespace prefix, or None if not found.
        """

        return element.nsmap.get(None)
