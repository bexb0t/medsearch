import argparse
import logging
from medsearch_api.app.logging_config import (
    configure_logging,
)
from medsearch_api.app.etl.update_spl_details import update_spl_data
from medsearch_api.run_api import create_app
from medsearch_api.app.etl.refresh_spl_list import update_spls


def run_refresh_spl_list(args):
    logger.debug("refresh_spl_list")

    logger.info(
        "Starting refresh_spl_list with new_records_only=%s, start_page=%s",
        args.new_records_only,
        args.start_page,
    )
    app = create_app()
    with app.app_context():
        update_spls(args.new_records_only, args.start_page)
    logger.info("Completed refresh_spl_list")


def run_update_spl_details(args):
    logger.info("Starting update_spl_details with pagesize=%s", args.pagesize)
    app = create_app()
    with app.app_context():
        update_spl_data(args.pagesize)
    logger.info("Completed update_spl_details")


def main():
    logger.debug("Debug log in main()")

    parser = argparse.ArgumentParser(description="ETL Entry Point for SPL Data")

    subparsers = parser.add_subparsers(dest="command")

    # Subparser for refresh_spl_list
    parser_refresh = subparsers.add_parser(
        "refresh_spl_list", help="Refresh the SPL list from DailyMed"
    )
    parser_refresh.add_argument(
        "-n",
        "--new-records-only",
        action="store_true",
        default=True,
        help="Only fetch new records (default: True)",
    )
    parser_refresh.add_argument(
        "-s", "--start-page", type=int, default=1, help="Start page number (default: 1)"
    )
    parser_refresh.set_defaults(func=run_refresh_spl_list)

    # Subparser for update_spl_details
    parser_update = subparsers.add_parser(
        "update_spl_details", help="Update SPL details"
    )
    parser_update.add_argument(
        "-p",
        "--pagesize",
        type=int,
        default=100,
        help="Page size for updating SPL details (default: 100)",
    )
    parser_update.set_defaults(func=run_update_spl_details)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    configure_logging()
    logger = logging.getLogger(__name__)

    logger.debug("Debug log in ___main__")
    # Initialize the Flask app
    app = create_app()

    # Use app context for operations that need it
    with app.app_context():
        main()  # Execute main logic within app context
