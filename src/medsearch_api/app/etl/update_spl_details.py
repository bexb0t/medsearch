import logging
from typing import Any, Dict, List, Generator
from medsearch_api.app.database.db_client import DBClient
from medsearch_api.app.database.models import SPL, Med
from sqlalchemy import func
from medsearch_api.app.etl.spl_detail_extractor import SPLDetailExtractor

logger = logging.getLogger(__name__)


def get_spls_to_update(
    pagesize: int = 50,
) -> Generator[List[Dict[str, Any]], None, None]:
    db_client = DBClient()

    offset = 0
    while True:
        # Use the DBClient to get the models with the required filters and pagination
        results = (
            db_client.session.query(SPL.id, Med.spl_id)
            .outerjoin(Med, SPL.id == Med.spl_id)
            .filter(
                (Med.updated_at.is_(None))
                | (
                    func.DATE_FORMAT(Med.updated_at, "%Y-%m-%d")
                    < func.DATE_FORMAT(SPL.updated_at, "%Y-%m-%d")
                )
            )
            .distinct()
            .order_by(SPL.id)
            .offset(offset)
            .limit(pagesize)
            .all()
        )

        if not results:
            break

        # Yield the results formatted as a list of dictionaries
        yield [{"spl_id": result[0], "set_id": result[1]} for result in results]
        offset += pagesize


def update_spl_data(pagesize: int = 50):
    total_processed = 0

    for spls in get_spls_to_update(pagesize):
        for spl in spls:
            spl_id = spl["spl_id"]
            set_id = spl["set_id"]
            extractor = SPLDetailExtractor(spl_id=spl_id, set_id=set_id)
            extractor.save_spl_details()
            total_processed += 1
    success_message = f"Successfully processed {total_processed} SPL records."
    logger.info(success_message)
