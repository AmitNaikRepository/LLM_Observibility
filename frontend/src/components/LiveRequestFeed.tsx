/**
 * Live Request Feed Component
 */

import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { CheckCircle, XCircle, AlertTriangle, Zap } from 'lucide-react';
import type { MetricsResponse } from '../types';

interface LiveRequestFeedProps {
  requests: MetricsResponse[];
}

export const LiveRequestFeed: React.FC<LiveRequestFeedProps> = ({ requests }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getStatusColor = (displayStatus: string) => {
    switch (displayStatus) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'slow':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="rounded-lg border-2 border-gray-200 bg-white p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Live Request Feed
        </h3>
        <div className="flex items-center text-sm text-gray-500">
          <Zap className="mr-1 h-4 w-4" />
          Auto-refresh every 5s
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Time
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                User
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Model
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Tokens
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Latency
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Cost
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {requests.map((request) => (
              <tr
                key={request.id}
                className={`border-l-4 ${getStatusColor(request.display_status)}`}
              >
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">
                  {formatDistanceToNow(new Date(request.timestamp), { addSuffix: true })}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm">
                  <div>
                    <div className="font-medium text-gray-900">{request.user_id}</div>
                    <div className="text-gray-500">{request.user_role}</div>
                  </div>
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">
                  {request.model.replace('llama-', '').replace('mixtral-', '')}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm">
                  <div className="text-gray-900">
                    {request.total_tokens.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">
                    {request.input_tokens} in / {request.output_tokens} out
                  </div>
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm">
                  <div className="font-medium text-gray-900">
                    {request.latency_ms}ms
                  </div>
                  {request.tokens_per_second && (
                    <div className="text-xs text-gray-500">
                      {request.tokens_per_second.toFixed(1)} t/s
                    </div>
                  )}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">
                  ${request.cost_usd.toFixed(6)}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm">
                  <div className="flex items-center">
                    {getStatusIcon(request.status)}
                    <span className="ml-2 capitalize">{request.status}</span>
                  </div>
                  {request.cache_hit && (
                    <div className="mt-1 text-xs text-purple-600">Cache Hit</div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {requests.length === 0 && (
        <div className="py-12 text-center text-gray-500">
          No requests to display. Generate some test traffic to see data here.
        </div>
      )}
    </div>
  );
};
