"""Migration: Add backgroundImage column to sigo_groups table"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

migration_sql = """
ALTER TABLE sigo_groups ADD COLUMN IF NOT EXISTS "backgroundImage" VARCHAR;
"""

try:
    with engine.connect() as connection:
        connection.execute(text(migration_sql))
        connection.commit()
        print("✅ Migration completed successfully: backgroundImage column added to sigo_groups table")
except Exception as e:
    print(f"❌ Migration failed: {e}")
