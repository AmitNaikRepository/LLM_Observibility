/**
 * Latency Trend Chart Component
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
    <div className="rounded-lg border-2 border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">
        Latency Trend (24 Hours)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(0)}ms`, '']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="avg_latency"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Avg Latency"
            dot={false}
          />
          {formattedData.some((d) => d.p95_latency) && (
            <Line
              type="monotone"
              dataKey="p95_latency"
              stroke="#ef4444"
              strokeWidth={2}
              strokeDasharray="5 5"
              name="P95 Latency"
              dot={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
