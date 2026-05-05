import logging
from src.db.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing database...")
    db = Database()
    logger.info("Database initialization complete.")

if __name__ == "__main__":
    main()
