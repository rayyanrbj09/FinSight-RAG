"""Database initialization script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import init_db

if __name__ == "__main__":
    print("🗄️  Initializing database...")
    init_db()
    print("✅ Database initialized successfully!")
