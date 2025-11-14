/**
 * Enhanced KPI Card Component
 */

import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple';
}

const colorClasses = {
  blue: 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 hover:border-blue-400',
  green: 'bg-gradient-to-br from-green-50 to-green-100 border-green-200 hover:border-green-400',
  red: 'bg-gradient-to-br from-red-50 to-red-100 border-red-200 hover:border-red-400',
  yellow: 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200 hover:border-yellow-400',
  purple: 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200 hover:border-purple-400',
};

const iconBgClasses = {
  blue: 'bg-gradient-to-br from-blue-500 to-blue-600',
  green: 'bg-gradient-to-br from-green-500 to-green-600',
  red: 'bg-gradient-to-br from-red-500 to-red-600',
  yellow: 'bg-gradient-to-br from-yellow-500 to-yellow-600',
  purple: 'bg-gradient-to-br from-purple-500 to-purple-600',
};

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  trend,
  trendValue,
  icon,
  color = 'blue',
}) => {
  return (
    <div className={`group rounded-2xl border-2 p-6 shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-2xl ${colorClasses[color]}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-semibold uppercase tracking-wide text-gray-600">{title}</p>
          <p className="mt-3 text-4xl font-extrabold text-gray-900">{value}</p>
          {subtitle && <p className="mt-2 text-sm font-medium text-gray-600">{subtitle}</p>}
          {trend && trendValue && (
            <div className="mt-3 flex items-center">
              {trend === 'up' ? (
                <div className="rounded-full bg-green-100 p-1">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                </div>
              ) : trend === 'down' ? (
                <div className="rounded-full bg-red-100 p-1">
                  <TrendingDown className="h-4 w-4 text-red-600" />
                </div>
              ) : null}
              <span
                className={`ml-2 text-sm font-semibold ${
                  trend === 'up'
                    ? 'text-green-600'
                    : trend === 'down'
                    ? 'text-red-600'
                    : 'text-gray-600'
                }`}
              >
                {trendValue}
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className={`rounded-xl p-4 text-white shadow-lg transition-transform duration-300 group-hover:scale-110 ${iconBgClasses[color]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};
