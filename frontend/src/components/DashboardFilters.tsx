/**
 * Dashboard Filters Component
 */

import React from 'react';
import { Filter } from 'lucide-react';

interface DashboardFiltersProps {
  dateRange: string;
  onDateRangeChange: (range: string) => void;
  selectedRole?: string;
  onRoleChange: (role: string) => void;
  selectedModel?: string;
  onModelChange: (model: string) => void;
  selectedStatus?: string;
  onStatusChange: (status: string) => void;
  roles: string[];
  models: string[];
}

export const DashboardFilters: React.FC<DashboardFiltersProps> = ({
  dateRange,
  onDateRangeChange,
  selectedRole,
  onRoleChange,
  selectedModel,
  onModelChange,
  selectedStatus,
  onStatusChange,
  roles,
  models,
}) => {
  return (
    <div className="rounded-lg border-2 border-gray-200 bg-white p-4">
      <div className="mb-3 flex items-center">
        <Filter className="mr-2 h-5 w-5 text-gray-600" />
        <h3 className="font-semibold text-gray-900">Filters</h3>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Date Range Filter */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Date Range
          </label>
          <select
            value={dateRange}
            onChange={(e) => onDateRangeChange(e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>

        {/* Role Filter */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            User Role
          </label>
          <select
            value={selectedRole || ''}
            onChange={(e) => onRoleChange(e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Roles</option>
            {roles.map((role) => (
              <option key={role} value={role}>
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Model Filter */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Model
          </label>
          <select
            value={selectedModel || ''}
            onChange={(e) => onModelChange(e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Models</option>
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Status
          </label>
          <select
            value={selectedStatus || ''}
            onChange={(e) => onStatusChange(e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="">All Statuses</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
            <option value="timeout">Timeout</option>
          </select>
        </div>
      </div>
    </div>
  );
};
