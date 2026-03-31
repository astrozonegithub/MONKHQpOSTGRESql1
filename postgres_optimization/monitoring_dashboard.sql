-- PostgreSQL Monitoring Dashboard Views
-- Compatible with both Neo and Koyeb environments

-- Create monitoring schema
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Database Overview View
CREATE OR REPLACE VIEW monitoring.database_overview AS
SELECT 
    'Database Overview' as category,
    'Database Size' as metric,
    pg_size_pretty(pg_database_size(current_database())) as value,
    CASE 
        WHEN pg_database_size(current_database()) > 2147483648 THEN 'High' -- > 2GB
        WHEN pg_database_size(current_database()) > 1073741824 THEN 'Medium' -- > 1GB
        ELSE 'Low'
    END as status,
    'Size of the database' as description
UNION ALL
SELECT 
    'Database Overview' as category,
    'Total Connections' as metric,
    count(*)::text as value,
    CASE 
        WHEN count(*) > 150 THEN 'High'
        WHEN count(*) > 100 THEN 'Medium'
        ELSE 'Low'
    END as status,
    'Total number of database connections' as description
FROM pg_stat_activity
UNION ALL
SELECT 
    'Database Overview' as category,
    'Active Connections' as metric,
    count(*)::text as value,
    CASE 
        WHEN count(*) > 50 THEN 'High'
        WHEN count(*) > 25 THEN 'Medium'
        ELSE 'Low'
    END as status,
    'Number of active database connections' as description
FROM pg_stat_activity
WHERE state = 'active'
UNION ALL
SELECT 
    'Database Overview' as category,
    'Cache Hit Ratio' as metric,
    ROUND((sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100, 2)::text as value,
    CASE 
        WHEN (sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100 < 95 THEN 'Low'
        WHEN (sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100 < 98 THEN 'Medium'
        ELSE 'High'
    END as status,
    'Buffer cache hit ratio (higher is better)' as description
FROM pg_stat_database
WHERE datname = current_database();

-- Performance Metrics View
CREATE OR REPLACE VIEW monitoring.performance_metrics AS
SELECT 
    'Performance' as category,
    'Slow Queries (>1s)' as metric,
    count(*)::text as value,
    CASE 
        WHEN count(*) > 10 THEN 'High'
        WHEN count(*) > 5 THEN 'Medium'
        ELSE 'Low'
    END as status,
    'Number of queries with average time > 1 second' as description
FROM pg_stat_statements
WHERE mean_exec_time > 1000
UNION ALL
SELECT 
    'Performance' as category,
    'Average Query Time' as metric,
    ROUND(mean(mean_exec_time), 2)::text as value,
    CASE 
        WHEN mean(mean_exec_time) > 500 THEN 'High'
        WHEN mean(mean_exec_time) > 100 THEN 'Medium'
        ELSE 'Low'
    END as status,
    'Average query execution time in milliseconds' as description
FROM pg_stat_statements
UNION ALL
SELECT 
    'Performance' as category,
    'Total Queries' as metric,
    sum(calls)::text as value,
    'N/A' as status,
    'Total number of queries executed' as description
FROM pg_stat_statements
UNION ALL
SELECT 
    'Performance' as category,
    'Lock Waits' as metric,
    count(*)::text as value,
    CASE 
        WHEN count(*) > 5 THEN 'High'
        WHEN count(*) > 0 THEN 'Medium'
        ELSE 'Low'
    END as status,
    'Number of processes waiting for locks' as description
FROM pg_locks
WHERE granted = false;

-- Storage Metrics View
CREATE OR REPLACE VIEW monitoring.storage_metrics AS
SELECT 
    'Storage' as category,
    'Total Tables' as metric,
    count(*)::text as value,
    'N/A' as status,
    'Total number of tables in the database' as description
FROM pg_tables
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
UNION ALL
SELECT 
    'Storage' as category,
    'Total Indexes' as metric,
    count(*)::text as value,
    'N/A' as status,
    'Total number of indexes in the database' as description
FROM pg_indexes
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
UNION ALL
SELECT 
    'Storage' as category,
    'Largest Table' as metric,
    tablename as value,
    'N/A' as status,
    'Largest table by size' as description
FROM (
    SELECT 
        tablename,
        pg_total_relation_size(schemaname||'.'||tablename) as size
    FROM pg_tables
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY size DESC
    LIMIT 1
) largest_table
UNION ALL
SELECT 
    'Storage' as category,
    'Unused Indexes' as metric,
    count(*)::text as value,
    CASE 
        WHEN count(*) > 5 THEN 'High'
        WHEN count(*) > 0 THEN 'Medium'
        ELSE 'Low'
    END as status,
    'Number of indexes that have never been used' as description
FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- Top Queries View
CREATE OR REPLACE VIEW monitoring.top_queries AS
SELECT 
    rank() OVER (ORDER BY total_exec_time DESC) as rank,
    LEFT(query, 100) as query_sample,
    calls,
    ROUND(total_exec_time, 2) as total_time_ms,
    ROUND(mean_exec_time, 2) as mean_time_ms,
    ROUND(rows, 0) as total_rows,
    pg_size_pretty(total_exec_time * 1024) as time_formatted
FROM pg_stat_statements
WHERE calls > 0
ORDER BY total_exec_time DESC
LIMIT 20;

-- Table Statistics View
CREATE OR REPLACE VIEW monitoring.table_statistics AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index Usage View
CREATE OR REPLACE VIEW monitoring.index_usage AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    CASE 
        WHEN idx_scan = 0 THEN 'Never Used'
        WHEN idx_scan < 10 THEN 'Low Usage'
        WHEN idx_scan < 100 THEN 'Medium Usage'
        ELSE 'High Usage'
    END as usage_category,
    ROUND((idx_scan::FLOAT / NULLIF((SELECT sum(calls) FROM pg_stat_statements), 0)) * 100, 2) as usage_percentage
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Connection Activity View
CREATE OR REPLACE VIEW monitoring.connection_activity AS
SELECT 
    state,
    count(*) as connection_count,
    ROUND((count(*)::FLOAT / (SELECT count(*) FROM pg_stat_activity)) * 100, 2) as percentage,
    array_agg(DISTINCT application_name) as applications,
    max(query_start) as latest_query_start
FROM pg_stat_activity
GROUP BY state
ORDER BY connection_count DESC;

-- Vacuum Analysis View
CREATE OR REPLACE VIEW monitoring.vacuum_analysis AS
SELECT 
    schemaname,
    tablename,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    ROUND((n_dead_tup::FLOAT / NULLIF(n_live_tup + n_dead_tup, 0)) * 100, 2) as dead_tuple_percentage,
    CASE 
        WHEN (n_dead_tup::FLOAT / NULLIF(n_live_tup + n_dead_tup, 0)) * 100 > 20 THEN 'Needs Vacuum'
        WHEN (n_dead_tup::FLOAT / NULLIF(n_live_tup + n_dead_tup, 0)) * 100 > 10 THEN 'Consider Vacuum'
        ELSE 'OK'
    END as vacuum_status,
    last_vacuum,
    last_autovacuum,
    CASE 
        WHEN last_autovacuum IS NULL THEN 'Never'
        WHEN last_autovacuum < now() - INTERVAL '7 days' THEN 'Old'
        ELSE 'Recent'
    END as autovacuum_status
FROM pg_stat_user_tables
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY dead_tuple_percentage DESC;

-- Replication Status View (for production)
CREATE OR REPLACE VIEW monitoring.replication_status AS
SELECT 
    'Replication' as category,
    'Standby Count' as metric,
    count(*)::text as value,
    CASE 
        WHEN count(*) = 0 THEN 'No Replication'
        WHEN count(*) = 1 THEN 'Single Standby'
        ELSE 'Multiple Standbys'
    END as status,
    'Number of standby servers' as description
FROM pg_stat_replication
UNION ALL
SELECT 
    'Replication' as category,
    'Replication Lag' as metric,
    EXTRACT(EPOCH FROM (pg_last_xact_replay_timestamp() - now()))::text as value,
    CASE 
        WHEN EXTRACT(EPOCH FROM (pg_last_xact_replay_timestamp() - now())) > 300 THEN 'High'
        WHEN EXTRACT(EPOCH FROM (pg_last_xact_replay_timestamp() - now())) > 60 THEN 'Medium'
        ELSE 'Low'
    END as status,
    'Replication lag in seconds' as description
WHERE EXISTS (SELECT 1 FROM pg_stat_replication);

-- Create a comprehensive dashboard summary
CREATE OR REPLACE VIEW monitoring.dashboard_summary AS
SELECT 
    category,
    count(*) as total_metrics,
    count(*) FILTER (WHERE status = 'High') as high_priority,
    count(*) FILTER (WHERE status = 'Medium') as medium_priority,
    count(*) FILTER (WHERE status = 'Low') as low_priority,
    CASE 
        WHEN count(*) FILTER (WHERE status = 'High') > 0 THEN 'Critical'
        WHEN count(*) FILTER (WHERE status = 'Medium') > 3 THEN 'Warning'
        ELSE 'Healthy'
    END as overall_status
FROM (
    SELECT * FROM monitoring.database_overview
    UNION ALL
    SELECT * FROM monitoring.performance_metrics
    UNION ALL
    SELECT * FROM monitoring.storage_metrics
) all_metrics
GROUP BY category
ORDER BY category;

-- Grant permissions to monitoring schema
GRANT USAGE ON SCHEMA monitoring TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA monitoring TO PUBLIC;

-- Create refresh function for updating statistics
CREATE OR REPLACE FUNCTION monitoring.refresh_statistics()
RETURNS void AS $$
BEGIN
    -- Refresh materialized views if any exist
    -- This function can be called periodically to update monitoring data
    
    -- Log the refresh
    INSERT INTO monitoring.log_table (timestamp, action) 
    VALUES (now(), 'Statistics refreshed');
    
    -- Analyze tables to update statistics
    ANALYZE;
END;
$$ LANGUAGE plpgsql;

-- Create log table for monitoring actions
CREATE TABLE IF NOT EXISTS monitoring.log_table (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT now(),
    action TEXT,
    details TEXT
);

-- Create index on log table
CREATE INDEX IF NOT EXISTS idx_log_table_timestamp ON monitoring.log_table(timestamp);

-- Comment on monitoring schema
COMMENT ON SCHEMA monitoring IS 'PostgreSQL monitoring dashboard views and functions';

-- Comments on important views
COMMENT ON VIEW monitoring.dashboard_summary IS 'Overall health summary of the database';
COMMENT ON VIEW monitoring.top_queries IS 'Top 20 slowest queries';
COMMENT ON VIEW monitoring.table_statistics IS 'Detailed table statistics';
COMMENT ON VIEW monitoring.index_usage IS 'Index usage analysis';
COMMENT ON VIEW monitoring.connection_activity IS 'Current connection activity';
COMMENT ON VIEW monitoring.vacuum_analysis IS 'Vacuum and dead tuple analysis';
