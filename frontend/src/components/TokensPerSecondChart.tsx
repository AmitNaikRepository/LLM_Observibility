/**
 * Tokens Per Second Chart Component
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
import type { TokensPerSecondData } from '../types';

interface TokensPerSecondChartProps {
  data: TokensPerSecondData[];
}

export const TokensPerSecondChart: React.FC<TokensPerSecondChartProps> = ({ data }) => {
  const formattedData = data.map((point) => ({
    ...point,
    time: format(new Date(point.timestamp), 'HH:mm'),
  }));

  return (
    <div className="rounded-lg border-2 border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">
        Tokens Per Second Trend
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis label={{ value: 'Tokens/sec', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(1)} t/s`, '']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="avg_tps"
            stroke="#8b5cf6"
            strokeWidth={2}
            name="Avg TPS"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
