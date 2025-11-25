-- Add backgroundImage column to sigo_groups table
ALTER TABLE sigo_groups ADD COLUMN IF NOT EXISTS "backgroundImage" VARCHAR;
