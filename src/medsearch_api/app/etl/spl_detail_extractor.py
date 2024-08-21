import logging
from typing import Optional
from sqlalchemy.exc import IntegrityError, DataError

from sqlalchemy.orm import Session
from medsearch_api.app.dailymed_response.dailymed_client import DailyMedClient
from medsearch_api.app.dailymed_response.spl_detail_response import (
    SPLDetailResponse,
)
from medsearch_api.app.database.db_client import DBClient
from medsearch_api.app.database.models import (
    MedForm,
    Med,
    MedOrganizationMap,
    Organization,
    SPLDataIssue,
)
from medsearch_api.app.db import db
from medsearch_api.app.custom_types import OperationType

logger = logging.getLogger(__name__)


class SPLDetailExtractor:
    def __init__(self, spl_id: int, set_id: str, db_client: Optional[DBClient] = None):
        self.session: Session = db.session
        self.spl_id: int = spl_id
        self.set_id: str = set_id
        self.endpoint = "spls/"
        self.db_client = db_client or DBClient()
        self.dailymed_client = DailyMedClient()
        logger.debug(
            f"SPLDetailParser Initialized. Instance variables: {self.__dict__}"
        )

    def fetch_document(self) -> Optional[SPLDetailResponse]:
        logger.debug("Fetching raw document.")

        # Fetch document using DailyMedClient
        raw_xml_response = self.dailymed_client.fetch_spl_by_set_id(self.set_id)

        if raw_xml_response:
            logger.debug("Document found. Returning SPLDetailResponse instance.")
            try:
                document = SPLDetailResponse(
                    raw_xml_response=raw_xml_response, spl_id=self.spl_id
                )
                return document
            except ValueError as ve:
                logger.error(f"Error parsing XML for SPL {self.spl_id}: {ve}")
                return None
        else:
            error_message = f"No response for SPL {self.spl_id}, set_id: {self.set_id}"
            self.log_spl_data_issue(
                operation_type=OperationType.download,
                table_name=None,
                message=error_message,
            )
            return None

    def save_spl_details(self) -> None:
        document = self.fetch_document()
        if document:
            med_form_id = self.get_or_create_med_form_id(document)
            med_id = self.create_or_save_med(document=document, med_form_id=med_form_id)
            org_id = self.get_or_create_organization(document)
            if med_id and org_id:
                self.create_med_organization_map(med_id, org_id)

    def create_or_save_med(
        self, document: SPLDetailResponse, med_form_id: Optional[int]
    ) -> Optional[int]:
        med = Med(
            spl_id=self.spl_id,
            med_form_id=med_form_id,
            code=document.med_code,
            code_system=document.med_code_system,
            name=document.med_name,
            generic_name=document.med_generic_name,
            effective_date=document.med_effective_date,
            version_number=document.med_version_number,
        )

        # Define filter criteria based on Med model's unique constraints
        filter_criteria = {
            "spl_id": self.spl_id,
            "code": document.med_code,
            "code_system": document.med_code_system,
            "effective_date": document.med_effective_date,
            "version_number": document.med_version_number,
        }
        try:
            updated_med = self.db_client.upsert_model(med, filter_criteria)
            return updated_med.id

        except (IntegrityError, DataError) as e:
            self.log_spl_data_issue(
                operation_type=OperationType.save,
                table_name=Med.__tablename__,
                message=str(e),
            )
            return None

    def get_or_create_med_form_id(self, document: SPLDetailResponse) -> Optional[int]:
        med_form_code = document.med_form_code
        med_form_code_system = document.med_form_code_system
        logger.debug(
            f"Looking for med form id for code {med_form_code}, system: {med_form_code_system}."
        )

        # Define filter criteria based on MedForm model's unique constraints
        filter_criteria = {
            "code": med_form_code,
            "code_system": med_form_code_system,
        }

        # Use get_model to query
        med_form = self.db_client.get_model(MedForm, filters=filter_criteria)

        if med_form:
            # Check if names match
            if med_form.name != document.med_form_name:
                logger.warn(
                    f"MedForm name mismatch for code {med_form_code} and system {med_form_code_system}."
                    f" SPL form name: {document.med_form_name}, DB form name: {med_form.name}"
                )
            logger.debug(f"Med form found with ID {med_form.id}")
            return int(med_form.id)
        else:
            try:
                # Create new MedForm entry
                logger.debug("Med form not found, adding.")
                new_med_form = MedForm(
                    code=document.med_form_code,
                    code_system=document.med_form_code_system,
                    name=document.med_form_name,
                )
                self.db_client.upsert_model(
                    new_med_form, filter_criteria
                )  # Use upsert for creating
                logger.debug(f"Created new MedForm entry: {new_med_form}")
                return int(new_med_form.id)
            except (IntegrityError, DataError) as e:
                self.session.rollback()
                self.log_spl_data_issue(
                    operation_type=OperationType.create,
                    table_name=MedForm.__tablename__,
                    message=str(e),
                )
                return None

    def create_med_organization_map(self, med_id: int, org_id: int) -> None:
        med_org_map = MedOrganizationMap(med_id=med_id, org_id=org_id)
        self.db_client.upsert_model(med_org_map, {"med_id": med_id, "org_id": org_id})
        logger.debug("Saved med_org_map record.")

    def get_or_create_organization(self, document: SPLDetailResponse) -> Optional[int]:
        filter_criteria = {
            "nih_id_extension": document.org_id_extension,
            "nih_id_root": document.org_id_root,
        }

        # Use get_model to query
        org = self.db_client.get_model(Organization, filters=filter_criteria)

        if org:
            if org.name != document.org_name:
                logger.warn(
                    f"Organization name mismatch for NIH ID extension {org.nih_id_extension} and root {org.nih_id_root}. SPL organization name: {document.org_name}, DB organization name: {org.name}"
                )
            return int(org.id)
        else:
            try:
                new_org = Organization(
                    name=document.org_name,
                    nih_id_extension=document.org_id_extension,
                    nih_id_root=document.org_id_root,
                )
                self.db_client.upsert_model(
                    new_org, filter_criteria
                )  # Use upsert for creating
                logger.debug(f"Created new Organization entry: {new_org}")
                return int(new_org.id)
            except (IntegrityError, DataError) as e:
                self.session.rollback()
                self.log_spl_data_issue(
                    operation_type=OperationType.create,
                    table_name=Organization.__tablename__,
                    message=str(e),
                )
                return None

    def log_spl_data_issue(
        self, operation_type: OperationType, table_name: Optional[str], message: str
    ) -> None:
        logger.error(
            f"Data error when extracting data from {self.spl_id}. operation_type: {operation_type}, table_name: {table_name}, message: {message}. Writing to spl_data_issues table."
        )
        data_issue = SPLDataIssue(
            spl_id=self.spl_id,
            operation_type=operation_type,
            table_name=table_name,
            error_message=message,
        )

        self.db_client.insert_model(data_issue)
