/**
 * Main Dashboard Application
 */

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  Activity,
  DollarSign,
  CheckCircle,
  TrendingUp,
  Database,
  Gauge,
  Sparkles,
} from 'lucide-react';
import { useDashboardData, useModels, useUserRoles } from './hooks/useDashboard';
import { KPICard } from './components/KPICard';
import { LatencyChart } from './components/LatencyChart';
import { CostPieChart } from './components/CostPieChart';
import { RequestVolumeChart } from './components/RequestVolumeChart';
import { TokensPerSecondChart } from './components/TokensPerSecondChart';
import { ErrorRateChart } from './components/ErrorRateChart';
import { LiveRequestFeed } from './components/LiveRequestFeed';
import { DashboardFilters } from './components/DashboardFilters';

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function DashboardContent() {
  const [dateRange, setDateRange] = useState('24h');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  // Fetch data with auto-refresh every 5 seconds
  const { data: dashboardData, isLoading, error } = useDashboardData(5000);
  const { data: models = [] } = useModels();
  const { data: roles = [] } = useUserRoles();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-t-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <div className="rounded-lg bg-red-50 border-2 border-red-200 p-6 text-center">
          <h2 className="mb-2 text-xl font-semibold text-red-900">
            Failed to load dashboard
          </h2>
          <p className="text-red-700">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </p>
          <p className="mt-4 text-sm text-red-600">
            Make sure the backend API is running on http://localhost:8000
          </p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { kpis, latency_trend, cost_by_model, request_volume, tokens_per_second, error_rate, recent_requests } =
    dashboardData;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                LLM Observability Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Real-time monitoring of your LLM infrastructure
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 animate-pulse rounded-full bg-green-500"></div>
              <span className="text-sm font-medium text-gray-600">Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* KPI Cards Row */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <KPICard
              title="Avg Latency"
              value={`${kpis.avg_latency_ms.toFixed(0)}ms`}
              subtitle={`P95: ${kpis.p95_latency_ms}ms`}
              icon={<Gauge className="h-6 w-6" />}
              color="blue"
            />
            <KPICard
              title="Total Cost Today"
              value={`$${kpis.total_cost_today.toFixed(4)}`}
              subtitle={`Saved: $${kpis.cost_savings_today.toFixed(4)}`}
              icon={<DollarSign className="h-6 w-6" />}
              color="green"
            />
            <KPICard
              title="Success Rate"
              value={`${kpis.success_rate.toFixed(1)}%`}
              subtitle={`${kpis.total_requests_today} requests today`}
              icon={<CheckCircle className="h-6 w-6" />}
              color="purple"
            />
            <KPICard
              title="Cache Hit Rate"
              value={`${kpis.cache_hit_rate.toFixed(1)}%`}
              subtitle={`${kpis.total_requests.toLocaleString()} total requests`}
              icon={<Database className="h-6 w-6" />}
              color="yellow"
            />
          </div>

          {/* Filters */}
          <DashboardFilters
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
            selectedRole={selectedRole}
            onRoleChange={setSelectedRole}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
            selectedStatus={selectedStatus}
            onStatusChange={setSelectedStatus}
            roles={roles}
            models={models}
          />

          {/* Charts Row 1 */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <LatencyChart data={latency_trend} />
            <CostPieChart data={cost_by_model} />
          </div>

          {/* Charts Row 2 */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <RequestVolumeChart data={request_volume} />
            <TokensPerSecondChart data={tokens_per_second} />
          </div>

          {/* Charts Row 3 */}
          <ErrorRateChart data={error_rate} />

          {/* Live Request Feed */}
          <LiveRequestFeed requests={recent_requests} />

          {/* Portfolio Feature: Cost Savings Banner */}
          {kpis.cost_savings_today > 0 && (
            <div className="rounded-lg border-2 border-green-200 bg-green-50 p-6">
              <div className="flex items-center">
                <Sparkles className="mr-3 h-8 w-8 text-green-600" />
                <div>
                  <h3 className="text-lg font-semibold text-green-900">
                    Smart Routing Savings
                  </h3>
                  <p className="mt-1 text-sm text-green-700">
                    AI Router saved ${kpis.cost_savings_today.toFixed(4)} today by
                    intelligently selecting optimal models - that's{' '}
                    {((kpis.cost_savings_today / (kpis.total_cost_today + kpis.cost_savings_today)) * 100).toFixed(1)}%
                    cost reduction vs. always using expensive models!
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 bg-white py-6">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            LLM Observability Dashboard - Powered by FastAPI, PostgreSQL, Redis, and LangFuse
          </p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardContent />
    </QueryClientProvider>
  );
}

export default App;
