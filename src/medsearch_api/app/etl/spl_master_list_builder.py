from datetime import datetime, date
import logging
from typing import Optional
from medsearch_api.app.dailymed_response.dailymed_client import DailyMedClient
from medsearch_api.app.dailymed_response.spl_list_response import (
    SPLListItemResponse,
    SPLListResponse,
)
from medsearch_api.app.database.db_client import DBClient
from medsearch_api.app.database.models import SPL

logger = logging.getLogger(__name__)


class SPLMasterListBuilder:
    def __init__(
        self,
        start_page: int,
        db_client: Optional[DBClient] = None,
        published_after: Optional[date] = None,
    ):
        self.page_number: int = start_page
        self.published_after: Optional[date] = published_after
        self.has_more_pages = True
        self.db_client = db_client or DBClient()
        self.dailymed_client = DailyMedClient()
        logger.info(f"SPLMasterListBuilder initiated: {self}")

    def fetch_next_page(self) -> Optional[SPLListResponse]:
        logger.info(f"Fetching page: {self.page_number}")
        response_content = self.dailymed_client.fetch_spls(
            page_number=self.page_number, published_after=self.published_after
        )
        if response_content:
            try:
                document = SPLListResponse(raw_xml_response=response_content)
                self.has_more_pages = document.has_more_pages
                if self.has_more_pages:
                    self.page_number += 1
                else:
                    logger.info("No more pages after this one.")
                return document
            except ValueError as ve:
                logger.error(f"Error parsing XML for SPL page {self.page_number}: {ve}")
                return None
        else:
            logger.error(f"No response for page {self.page_number}")
            return None

    def save_spl_list_item(self, spl_item: SPLListItemResponse) -> bool:
        """Saves an SPL list item to the database."""
        published_date = datetime.strptime(spl_item.published_date, "%b %d, %Y")

        spl = SPL(
            set_id=spl_item.set_id,
            title=spl_item.title,
            published_date=published_date,
        )

        try:
            self.db_client.upsert_model(spl, {"set_id": spl.set_id})
            return True
        except Exception as e:
            logger.error(f"Error saving SPL record with Set ID {spl.set_id}: {e}")
            return False

    def save_page_data(self, document: SPLListResponse) -> int:
        """Saves the SPL entries parsed from a single page.

        Args:
            document: The SPLListResponse object containing page data.

        Returns:
            int: The number of SPL entries saved.
        """

        saved_count = 0
        for spl_item in document.spl_list_items:
            saved_count += self.save_spl_list_item(spl_item)
        return saved_count
