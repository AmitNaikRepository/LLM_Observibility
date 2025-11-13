/**
 * Error Rate Chart Component
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import type { ErrorRateData } from '../types';

interface ErrorRateChartProps {
  data: ErrorRateData[];
}

export const ErrorRateChart: React.FC<ErrorRateChartProps> = ({ data }) => {
  const formattedData = data.map((point) => ({
    ...point,
    time: format(new Date(point.timestamp), 'HH:mm'),
  }));

  return (
    <div className="rounded-lg border-2 border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">Error Rate Over Time</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis label={{ value: 'Error Rate (%)', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(2)}%`, '']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="error_rate"
            stroke="#ef4444"
            strokeWidth={2}
            name="Error Rate"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
