/**
 * Cost Breakdown Pie Chart Component
 */

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import type { CostByModel } from '../types';

interface CostPieChartProps {
  data: CostByModel[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export const CostPieChart: React.FC<CostPieChartProps> = ({ data }) => {
  const chartData = data.map((item) => ({
    name: item.model.replace('llama-', '').replace('mixtral-', ''),
    value: item.cost,
    percentage: item.percentage,
  }));

  return (
    <div className="rounded-lg border-2 border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">
        Cost Breakdown by Model
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => [`$${value.toFixed(6)}`, 'Cost']}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div key={item.model} className="flex items-center justify-between text-sm">
            <div className="flex items-center">
              <div
                className="mr-2 h-3 w-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="font-medium">{item.model}</span>
            </div>
            <span className="text-gray-600">
              ${item.cost.toFixed(6)} ({item.request_count} requests)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
