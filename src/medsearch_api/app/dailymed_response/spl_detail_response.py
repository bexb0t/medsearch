import logging
from typing import Dict, Optional
from medsearch_api.app.dailymed_response.base_dailymed_response import (
    BaseDailyMedResponse,
)
from medsearch_api.app.db import db
from medsearch_api.app.database.models import SPLParsingIssue
from medsearch_api.app.xml.utils import (
    XMLLocation,
    get_document_content,
    get_document_structure,
)


logger = logging.getLogger(__name__)


class SPLDetailResponse(BaseDailyMedResponse):
    """Handles the detail response for a SPL (Structured Product Label)."""

    # define the attributes we are tracking
    med_code: Optional[str] = None
    med_code_system: Optional[str] = None
    med_name: Optional[str] = None
    med_effective_date: Optional[str] = None
    med_version_number: Optional[str] = None
    med_generic_name: Optional[str] = None
    med_form_name: Optional[str] = None
    med_form_code: Optional[str] = None
    med_form_code_system: Optional[str] = None
    org_name: Optional[str] = None
    org_id_extension: Optional[str] = None
    org_id_root: Optional[str] = None

    # specify the locations of these attributes
    xml_fields: Dict[str, XMLLocation] = {
        "med_code": XMLLocation(xpath="v3:code", attrib="code"),
        "med_code_system": XMLLocation(xpath="v3:code", attrib="codeSystem"),
        "med_name": XMLLocation(xpath=".//v3:manufacturedProduct/v3:name", attrib=None),
        "med_effective_date": XMLLocation(xpath="v3:effectiveTime", attrib="value"),
        "med_version_number": XMLLocation(xpath="v3:versionNumber", attrib="value"),
        "med_generic_name": XMLLocation(
            xpath=".//v3:genericMedicine/v3:name", attrib=None
        ),
        "med_form_name": XMLLocation(
            xpath=".//v3:manufacturedProduct/v3:formCode", attrib="displayName"
        ),
        "med_form_code": XMLLocation(
            xpath=".//v3:manufacturedProduct/v3:formCode", attrib="code"
        ),
        "med_form_code_system": XMLLocation(
            xpath=".//v3:manufacturedProduct/v3:formCode", attrib="codeSystem"
        ),
        "org_name": XMLLocation(
            xpath=".//v3:assignedEntity/v3:representedOrganization/v3:name", attrib=None
        ),
        "org_id_extension": XMLLocation(
            xpath=".//v3:assignedEntity/v3:representedOrganization/v3:id",
            attrib="extension",
        ),
        "org_id_root": XMLLocation(
            xpath=".//v3:assignedEntity/v3:representedOrganization/v3:id", attrib="root"
        ),
    }

    def __init__(self, raw_xml_response: bytes, spl_id: int):
        self.spl_id = spl_id
        super().__init__(raw_xml_response)

        logger.debug(f"Created SPLDetailResponse instance {self}")

    def log_xml_parsing_issue(self, error: ValueError):
        """Logs XML parsing issues and saves details to the database.

        Args:
            error (ValueError): The error encountered during XML parsing.
        """
        error_message = str(error)
        logger.error(
            f"Error parsing XML for SPL ID {self.spl_id}: {error_message}. Writing to spl_parsing_issues table."
        )

        # Log the XML content and structure
        xml_content = get_document_content(self.document)
        xml_structure = get_document_structure(self.document)

        # Save the error details to the database
        parsing_issue = SPLParsingIssue(
            spl_id=self.spl_id,
            error=error_message,
            xml_content=xml_content,
            xml_structure=xml_structure,
        )
        db.session.add(parsing_issue)
        db.session.commit()
