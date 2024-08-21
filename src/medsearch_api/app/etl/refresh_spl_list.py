import logging

from typing import Optional
from datetime import datetime, timedelta

from medsearch_api.app.etl.spl_master_list_builder import SPLMasterListBuilder
from medsearch_api.app.database.models import SPL
from medsearch_api.app.database.db_client import DBClient

logger = logging.getLogger(__name__)


def get_latest_published_date() -> Optional[datetime]:
    latest_spl = SPL.query.order_by(SPL.published_date.desc()).first()
    if latest_spl:
        return latest_spl.published_date
    return None


def update_spls(new_records_only: bool = True, start_page: int = 1) -> None:
    """Fetches and saves SPLs from DailyMed incrementally.

    Args:
        new_records_only (bool, optional): If True, only fetches records published
            after the latest record in the database. Defaults to True.
        start_page (int, optional): The page number to start fetching from.
            Defaults to 1.
    """

    logger.debug("Debug log in update_spls")

    data_access = DBClient()
    if new_records_only:
        latest_published_date: Optional[datetime] = get_latest_published_date()
        if latest_published_date:
            published_after = latest_published_date - timedelta(days=3)
            logger.info(f"Fetching records after {str(published_after)}.")
        else:
            published_after = None  # No records in database, fetch all
            logger.info("Fetching all records")
    builder = SPLMasterListBuilder(
        db_client=data_access,
        start_page=start_page,
        published_after=published_after,
    )

    saved_count = 0
    while builder.has_more_pages:
        page_data = builder.fetch_next_page()
        if page_data:
            saved_count += builder.save_page_data(page_data)

    logging.info(f"Finished fetching and saving {saved_count} SPLs.")
