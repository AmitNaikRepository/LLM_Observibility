-- LLM Observability Database Schema

-- Main metrics table
CREATE TABLE IF NOT EXISTS llm_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id VARCHAR(50) NOT NULL,
    user_role VARCHAR(20) NOT NULL,
    model VARCHAR(50) NOT NULL,
    input_tokens INT NOT NULL,
    output_tokens INT NOT NULL,
    total_tokens INT GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    latency_ms INT NOT NULL,
    ttft_ms INT,
    tokens_per_second FLOAT,
    cost_usd DECIMAL(10,8) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_type VARCHAR(100),
    error_message TEXT,
    component VARCHAR(50) NOT NULL,
    cache_hit BOOLEAN DEFAULT FALSE,
    trace_id VARCHAR(100),
    span_id VARCHAR(100),
    request_id VARCHAR(100) UNIQUE,
    prompt_tokens INT,
    completion_tokens INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_timestamp ON llm_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_id ON llm_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_model ON llm_metrics(model);
CREATE INDEX IF NOT EXISTS idx_status ON llm_metrics(status);
CREATE INDEX IF NOT EXISTS idx_component ON llm_metrics(component);
CREATE INDEX IF NOT EXISTS idx_user_role ON llm_metrics(user_role);
CREATE INDEX IF NOT EXISTS idx_trace_id ON llm_metrics(trace_id);
CREATE INDEX IF NOT EXISTS idx_timestamp_status ON llm_metrics(timestamp DESC, status);

-- Security layer events table
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    request_id VARCHAR(100) REFERENCES llm_metrics(request_id),
    layer VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    user_role VARCHAR(20) NOT NULL,
    details JSONB,
    blocked BOOLEAN DEFAULT FALSE,
    threat_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_security_layer ON security_events(layer);
CREATE INDEX IF NOT EXISTS idx_security_request ON security_events(request_id);

-- Model routing decisions table
CREATE TABLE IF NOT EXISTS routing_decisions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    request_id VARCHAR(100) REFERENCES llm_metrics(request_id),
    user_id VARCHAR(50) NOT NULL,
    selected_model VARCHAR(50) NOT NULL,
    alternative_models JSONB,
    selection_reason VARCHAR(200),
    estimated_cost DECIMAL(10,8),
    actual_cost DECIMAL(10,8),
    cost_savings DECIMAL(10,8),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_routing_timestamp ON routing_decisions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_routing_model ON routing_decisions(selected_model);

-- Cache statistics table
CREATE TABLE IF NOT EXISTS cache_stats (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    request_id VARCHAR(100) REFERENCES llm_metrics(request_id),
    user_id VARCHAR(50) NOT NULL,
    cache_key VARCHAR(200),
    hit BOOLEAN NOT NULL,
    similarity_score FLOAT,
    tokens_saved INT DEFAULT 0,
    cost_saved DECIMAL(10,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cache_timestamp ON cache_stats(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cache_hit ON cache_stats(hit);

-- Aggregated daily stats for faster queries
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_requests INT DEFAULT 0,
    successful_requests INT DEFAULT 0,
    failed_requests INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    total_cost DECIMAL(12,6) DEFAULT 0,
    avg_latency_ms FLOAT DEFAULT 0,
    p95_latency_ms INT DEFAULT 0,
    p99_latency_ms INT DEFAULT 0,
    cache_hit_rate FLOAT DEFAULT 0,
    cost_savings DECIMAL(12,6) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_stats(date DESC);

-- Model usage stats
CREATE TABLE IF NOT EXISTS model_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    model VARCHAR(50) NOT NULL,
    request_count INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    total_cost DECIMAL(12,6) DEFAULT 0,
    avg_latency_ms FLOAT DEFAULT 0,
    success_rate FLOAT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, model)
);

CREATE INDEX IF NOT EXISTS idx_model_stats_date ON model_stats(date DESC);
CREATE INDEX IF NOT EXISTS idx_model_stats_model ON model_stats(model);

-- PII detection events
CREATE TABLE IF NOT EXISTS pii_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    request_id VARCHAR(100) REFERENCES llm_metrics(request_id),
    user_id VARCHAR(50) NOT NULL,
    pii_types JSONB NOT NULL,
    masked_count INT DEFAULT 0,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pii_timestamp ON pii_events(timestamp DESC);

-- Rate limit tracking
CREATE TABLE IF NOT EXISTS rate_limits (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    request_count INT DEFAULT 0,
    limit_exceeded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, endpoint, window_start)
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_user ON rate_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON rate_limits(window_start DESC);

-- Create views for common queries
CREATE OR REPLACE VIEW v_recent_requests AS
SELECT
    lm.id,
    lm.timestamp,
    lm.user_id,
    lm.user_role,
    lm.model,
    lm.input_tokens,
    lm.output_tokens,
    lm.total_tokens,
    lm.latency_ms,
    lm.cost_usd,
    lm.status,
    lm.component,
    lm.cache_hit,
    CASE
        WHEN lm.latency_ms > 2000 THEN 'slow'
        WHEN lm.status = 'error' THEN 'error'
        ELSE 'success'
    END as display_status
FROM llm_metrics lm
ORDER BY lm.timestamp DESC
LIMIT 100;

CREATE OR REPLACE VIEW v_hourly_stats AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as request_count,
    AVG(latency_ms) as avg_latency,
    SUM(cost_usd) as total_cost,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate,
    AVG(tokens_per_second) as avg_tokens_per_second
FROM llm_metrics
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- Function to calculate percentiles
CREATE OR REPLACE FUNCTION calculate_percentile(p FLOAT)
RETURNS TABLE(percentile_value INT) AS $$
BEGIN
    RETURN QUERY
    SELECT PERCENTILE_CONT(p) WITHIN GROUP (ORDER BY latency_ms)::INT
    FROM llm_metrics
    WHERE timestamp > NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- Function to update daily stats (call this periodically)
CREATE OR REPLACE FUNCTION update_daily_stats() RETURNS void AS $$
DECLARE
    target_date DATE := CURRENT_DATE;
BEGIN
    INSERT INTO daily_stats (
        date,
        total_requests,
        successful_requests,
        failed_requests,
        total_tokens,
        total_cost,
        avg_latency_ms,
        p95_latency_ms,
        p99_latency_ms,
        cache_hit_rate,
        cost_savings
    )
    SELECT
        target_date,
        COUNT(*),
        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END),
        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END),
        SUM(total_tokens),
        SUM(cost_usd),
        AVG(latency_ms),
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)::INT,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms)::INT,
        AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END),
        SUM(COALESCE((SELECT cost_saved FROM cache_stats cs WHERE cs.request_id = lm.request_id), 0))
    FROM llm_metrics lm
    WHERE DATE(timestamp) = target_date
    ON CONFLICT (date)
    DO UPDATE SET
        total_requests = EXCLUDED.total_requests,
        successful_requests = EXCLUDED.successful_requests,
        failed_requests = EXCLUDED.failed_requests,
        total_tokens = EXCLUDED.total_tokens,
        total_cost = EXCLUDED.total_cost,
        avg_latency_ms = EXCLUDED.avg_latency_ms,
        p95_latency_ms = EXCLUDED.p95_latency_ms,
        p99_latency_ms = EXCLUDED.p99_latency_ms,
        cache_hit_rate = EXCLUDED.cache_hit_rate,
        cost_savings = EXCLUDED.cost_savings,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
