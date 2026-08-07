"""Database initialization script."""

import sys
from pathlib import Path
import logging


sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import *
from db.database import *
from db.crud import *

logger = get_logger(__name__)
if __name__ == "__main__":
    logger.info("🗄️  Initializing database...")
    ini = init_db()
    print("✅ Database initialized successfully!")
    print(get_database_url())
    print("Get database info:")
    print(get_db())
    print("Get all companies:")
    db = next(get_db())
    create_company(db, "Test Company3222")
    logger.info("Get all companies:")
    companies = get_all_companies(db)
     # I wantr to see the name of the first company in the database, or a message if there are no companies.
    if companies:
        for _ in companies:
            print(f"Company ID: {_ .id}, Company Name: {_ .name}")
        
    else:
        print("No companies found in the database.")