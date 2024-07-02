from flask import Flask
import logging
from medsearch_api.app.db import db
from medsearch_api.app.config import settings

from medsearch_api.app.database.utils import verify_database

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance outside create_app()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(settings)

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    return app


if __name__ == "__main__":
    verify_database()
    app = create_app()

    # Ensure to use app context for database operations
    with app.app_context():
        app.run(host="0.0.0.0")
