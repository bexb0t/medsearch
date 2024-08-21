from lxml import etree
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class XMLLocation:
    def __init__(self, xpath: str, attrib: Optional[str]):
        self.xpath = xpath
        self.attrib = attrib


def get_xml_value(document: etree._Element, location: XMLLocation) -> Optional[str]:
    try:
        logger.debug(f"Trying to find element with xpath: {location.xpath}")
        element = document.find(location.xpath, {"v3": "urn:hl7-org:v3"})
        if element is None:
            raise ValueError(f"Xpath {location.xpath} not found in document.")

        if location.attrib:
            value = element.attrib.get(location.attrib)
            if not value:
                raise ValueError(
                    f"Attribute {location.attrib} not found on xpath {location.xpath}"
                )
        else:
            value = element.text
            if not value:
                raise ValueError(f"No text found at xpath {location.xpath}")

        return value
    except ValueError as ve:
        raise ve


def get_document_content(document: etree._Element) -> str:
    return etree.tostring(document, encoding="unicode")


def get_document_structure(document: etree._Element) -> str:
    structure_str = []

    stack = [(document, "v3")]
    while stack:
        elem, ns_prefix = stack.pop()
        tag_name = normalize_tag(elem.tag)
        current_path = f"{ns_prefix}:{tag_name}"

        if elem.text and elem.text.strip():
            structure_str.append(
                f"TAG: {tag_name}, VALUE: {elem.text.strip()} - Namespace: {ns_prefix if ns_prefix else 'No namespace'} - absolute xpath: {current_path}, attrib: None"
            )

        for attrib, value in elem.attrib.items():
            structure_str.append(
                f"TAG: {tag_name}, VALUE: {value} - Namespace: {ns_prefix if ns_prefix else 'No namespace'} - absolute xpath: {current_path}, attrib: {attrib}"
            )

        for child in elem:
            child_ns_prefix = get_namespace_prefix(child.tag)
            stack.append((child, child_ns_prefix))

    return "\n".join(structure_str)


def normalize_tag(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def get_namespace_prefix(tag: str) -> str:
    if "}" in tag:
        ns_uri = tag.split("}", 1)[0].strip("{")
        return "v3" if ns_uri == "urn:hl7-org:v3" else ns_uri
    return ""
