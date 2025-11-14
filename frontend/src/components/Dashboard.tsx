/**
 * Enhanced Dashboard Component with Beautiful UI
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DollarSign,
  CheckCircle,
  Database,
  Gauge,
  Sparkles,
  Home,
  RefreshCw,
  Download,
} from 'lucide-react';
import { useDashboardData, useModels, useUserRoles } from '../hooks/useDashboard';
import { KPICard } from './KPICard';
import { LatencyChart } from './LatencyChart';
import { CostPieChart } from './CostPieChart';
import { RequestVolumeChart } from './RequestVolumeChart';
import { TokensPerSecondChart } from './TokensPerSecondChart';
import { ErrorRateChart } from './ErrorRateChart';
import { LiveRequestFeed } from './LiveRequestFeed';
import { DashboardFilters } from './DashboardFilters';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dateRange, setDateRange] = useState('24h');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  // Fetch data with auto-refresh every 5 seconds
  const { data: dashboardData, isLoading, error, refetch } = useDashboardData(5000);
  const { data: models = [] } = useModels();
  const { data: roles = [] } = useUserRoles();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center">
          <div className="relative mb-8">
            <div className="h-20 w-20 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Gauge className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h3 className="mb-2 text-xl font-semibold text-gray-900">Loading Dashboard</h3>
          <p className="text-gray-600">Fetching real-time metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-md rounded-2xl border-2 border-red-200 bg-white p-8 shadow-2xl">
          <div className="mb-4 flex justify-center">
            <div className="rounded-full bg-red-100 p-4">
              <CheckCircle className="h-12 w-12 text-red-600" />
            </div>
          </div>
          <h2 className="mb-3 text-center text-2xl font-bold text-gray-900">
            Connection Error
          </h2>
          <p className="mb-4 text-center text-gray-700">
            {error instanceof Error ? error.message : 'Failed to load dashboard data'}
          </p>
          <div className="rounded-lg bg-red-50 p-4">
            <p className="text-sm text-red-700">
              <strong>Troubleshooting:</strong>
              <br />
              • Make sure the backend is running on http://localhost:8000
              <br />
              • Check if PostgreSQL and Redis are running
              <br />• Run: <code className="rounded bg-red-100 px-1">docker-compose up -d</code>
            </p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 w-full rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-blue-700"
          >
            Retry Connection
          </button>
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Enhanced Header */}
      <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-lg shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center gap-2 rounded-lg border-2 border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 transition-all hover:border-blue-600 hover:text-blue-600"
              >
                <Home className="h-4 w-4" />
                Home
              </button>
              <div className="h-8 w-px bg-gray-300" />
              <div>
                <h1 className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-2xl font-bold text-transparent sm:text-3xl">
                  LLM Observability Dashboard
                </h1>
                <p className="text-sm text-gray-600">Real-time monitoring & analytics</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={() => refetch()}
                className="flex items-center gap-2 rounded-lg border-2 border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 transition-all hover:border-blue-600 hover:text-blue-600"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </button>
              <div className="flex items-center gap-2 rounded-full bg-green-100 px-4 py-2">
                <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-green-500"></div>
                <span className="text-sm font-semibold text-green-700">Live</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {/* Welcome Banner */}
          <div className="overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-white shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="mb-2 text-3xl font-bold">Welcome to Your Dashboard</h2>
                <p className="text-blue-100">
                  Monitoring {kpis.total_requests.toLocaleString()} total requests with{' '}
                  {kpis.success_rate.toFixed(1)}% success rate
                </p>
              </div>
              <div className="hidden rounded-2xl bg-white/10 p-6 backdrop-blur-sm md:block">
                <Sparkles className="h-16 w-16" />
              </div>
            </div>
          </div>

          {/* KPI Cards Row */}
          <div>
            <h3 className="mb-4 text-lg font-semibold text-gray-900">Key Performance Indicators</h3>
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
          </div>

          {/* Filters */}
          <div>
            <h3 className="mb-4 text-lg font-semibold text-gray-900">Filter & Analyze</h3>
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
          </div>

          {/* Charts Section */}
          <div>
            <h3 className="mb-4 text-lg font-semibold text-gray-900">Performance Analytics</h3>
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <LatencyChart data={latency_trend} />
              <CostPieChart data={cost_by_model} />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <RequestVolumeChart data={request_volume} />
            <TokensPerSecondChart data={tokens_per_second} />
          </div>

          <ErrorRateChart data={error_rate} />

          {/* Cost Savings Banner */}
          {kpis.cost_savings_today > 0 && (
            <div className="overflow-hidden rounded-2xl border-2 border-green-200 bg-gradient-to-r from-green-50 to-emerald-50 p-6 shadow-lg">
              <div className="flex items-center gap-4">
                <div className="flex-shrink-0 rounded-xl bg-green-100 p-4">
                  <Sparkles className="h-8 w-8 text-green-600" />
                </div>
                <div className="flex-1">
                  <h3 className="mb-1 text-xl font-bold text-green-900">
                    AI Router Optimization
                  </h3>
                  <p className="text-green-700">
                    Saved <span className="font-bold">${kpis.cost_savings_today.toFixed(4)}</span>{' '}
                    today through intelligent model selection - that's{' '}
                    <span className="font-bold">
                      {((kpis.cost_savings_today / (kpis.total_cost_today + kpis.cost_savings_today)) * 100).toFixed(1)}%
                    </span>{' '}
                    cost reduction vs. always using expensive models!
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Live Request Feed */}
          <div>
            <h3 className="mb-4 text-lg font-semibold text-gray-900">Live Request Feed</h3>
            <LiveRequestFeed requests={recent_requests} />
          </div>
        </div>
      </main>

      {/* Enhanced Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-sm text-gray-600">
              LLM Observability Dashboard - Powered by{' '}
              <span className="font-semibold text-blue-600">FastAPI</span>,{' '}
              <span className="font-semibold text-blue-600">PostgreSQL</span>,{' '}
              <span className="font-semibold text-blue-600">Redis</span>, and{' '}
              <span className="font-semibold text-blue-600">LangFuse</span>
            </p>
            <p className="mt-2 text-xs text-gray-500">
              Auto-refreshing every 5 seconds • Last updated: {new Date().toLocaleTimeString()}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};
