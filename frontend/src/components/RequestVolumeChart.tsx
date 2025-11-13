/**
 * Request Volume Bar Chart Component
 */

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import type { RequestVolume } from '../types';

interface RequestVolumeChartProps {
  data: RequestVolume[];
}

export const RequestVolumeChart: React.FC<RequestVolumeChartProps> = ({ data }) => {
  const formattedData = data.map((point) => ({
    ...point,
    time: format(new Date(point.hour), 'HH:mm'),
  }));

  return (
    <div className="rounded-lg border-2 border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">
        Request Volume by Hour
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis label={{ value: 'Requests', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="success_count" stackId="a" fill="#10b981" name="Success" />
          <Bar dataKey="error_count" stackId="a" fill="#ef4444" name="Error" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
