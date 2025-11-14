/**
 * Enhanced Latency Trend Chart Component
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { Activity } from 'lucide-react';
import type { LatencyDataPoint } from '../types';

interface LatencyChartProps {
  data: LatencyDataPoint[];
}

export const LatencyChart: React.FC<LatencyChartProps> = ({ data }) => {
  const formattedData = data.map((point) => ({
    ...point,
    time: format(new Date(point.timestamp), 'HH:mm'),
  }));

  return (
    <div className="group rounded-2xl border-2 border-gray-200 bg-white p-6 shadow-lg transition-all duration-300 hover:shadow-2xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900">
            Latency Trend
          </h3>
          <p className="text-sm text-gray-600">Last 24 hours performance</p>
        </div>
        <div className="rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 p-3 text-white shadow-lg">
          <Activity className="h-6 w-6" />
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <defs>
            <linearGradient id="colorAvg" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: '12px' }} />
          <YAxis
            label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft', style: { fill: '#6b7280' } }}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(0)}ms`, '']}
            labelFormatter={(label) => `Time: ${label}`}
            contentStyle={{
              backgroundColor: 'white',
              border: '2px solid #e5e7eb',
              borderRadius: '12px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
          <Line
            type="monotone"
            dataKey="avg_latency"
            stroke="#3b82f6"
            strokeWidth={3}
            name="Avg Latency"
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
          />
          {formattedData.some((d) => d.p95_latency) && (
            <Line
              type="monotone"
              dataKey="p95_latency"
              stroke="#ef4444"
              strokeWidth={3}
              strokeDasharray="8 4"
              name="P95 Latency"
              dot={{ fill: '#ef4444', r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
