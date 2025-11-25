"""Migration: Create sigo_dashboards table"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

migration_sql = """
CREATE TABLE IF NOT EXISTS sigo_dashboards (
    "dashboardId" VARCHAR PRIMARY KEY,
    "dashboardName" VARCHAR NOT NULL,
    "workspaceId" VARCHAR NOT NULL,
    "workspaceName" VARCHAR,
    "groupId" INTEGER REFERENCES sigo_groups("groupId") ON DELETE SET NULL,
    "backgroundImage" VARCHAR,
    "pipelineId" VARCHAR,
    "embedUrl" VARCHAR,
    "webUrl" VARCHAR,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "lastUpdatedAt" TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_dashboards_dashboard_id ON sigo_dashboards("dashboardId");
CREATE INDEX IF NOT EXISTS idx_dashboards_workspace_id ON sigo_dashboards("workspaceId");
CREATE INDEX IF NOT EXISTS idx_dashboards_group_id ON sigo_dashboards("groupId");
"""

try:
    with engine.connect() as connection:
        connection.execute(text(migration_sql))
        connection.commit()
        print("✅ Migration completed successfully: sigo_dashboards table created")
except Exception as e:
    print(f"❌ Migration failed: {e}")
