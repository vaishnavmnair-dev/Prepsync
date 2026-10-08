-- ============================================================================
-- PROJECT: BRIDGING THE GAP BETWEEN COLLEGE WORK AND PLACEMENT PREPARATION
-- MASTER INITIALIZATION SCRIPT
-- ============================================================================
-- Execute all database setup files in order using psql:
--   psql -U <username> -d <database_name> -f init_database.sql
-- ============================================================================

\echo '=================================================='
\echo '1/5: Creating Tables, Types, Triggers, & Indexes...'
\echo '=================================================='
\i 01_schema.sql

\echo '=================================================='
\echo '2/5: Creating Views & AI Context Functions...'
\echo '=================================================='
\i 02_views_and_functions.sql

\echo '=================================================='
\echo '3/5: Seeding Realistic Student & Curriculum Data...'
\echo '=================================================='
\i 03_seed_data.sql

\echo '=================================================='
\echo '4/5: Running Example Verification Queries...'
\echo '=================================================='
\i 04_example_queries.sql

\echo '=================================================='
\echo '5/5: Executing Master AI Daily Planning Query...'
\echo '=================================================='
\i 05_ai_planning_context.sql

\echo '=================================================='
\echo 'Database initialization complete!'
\echo '=================================================='

