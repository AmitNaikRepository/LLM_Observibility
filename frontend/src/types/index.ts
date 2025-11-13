/**
 * TypeScript types for LLM Observability Dashboard
 */

export interface KPIMetrics {
  avg_latency_ms: number;
  p95_latency_ms: number;
  total_cost_today: number;
  success_rate: number;
  total_requests: number;
  total_requests_today: number;
  cache_hit_rate: number;
  cost_savings_today: number;
}

export interface LatencyDataPoint {
  timestamp: string;
  avg_latency: number;
  p95_latency?: number;
}

export interface CostByModel {
  model: string;
  cost: number;
  percentage: number;
  request_count: number;
}

export interface RequestVolume {
  hour: string;
  request_count: number;
  success_count: number;
  error_count: number;
}

export interface TokensPerSecondData {
  timestamp: string;
  avg_tps: number;
}

export interface ErrorRateData {
  timestamp: string;
  error_rate: number;
  total_requests: number;
  error_count: number;
}

export interface MetricsResponse {
  id: number;
  timestamp: string;
  user_id: string;
  user_role: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  latency_ms: number;
  ttft_ms?: number;
  tokens_per_second?: number;
  cost_usd: number;
  status: string;
  error_type?: string;
  component: string;
  cache_hit: boolean;
  display_status: string;
}

export interface DashboardData {
  kpis: KPIMetrics;
  latency_trend: LatencyDataPoint[];
  cost_by_model: CostByModel[];
  request_volume: RequestVolume[];
  tokens_per_second: TokensPerSecondData[];
  error_rate: ErrorRateData[];
  recent_requests: MetricsResponse[];
}

export interface DashboardFilters {
  dateRange: '1h' | '24h' | '7d' | '30d';
  userRole?: string;
  model?: string;
  status?: string;
}
