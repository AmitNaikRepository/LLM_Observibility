/**
 * API service for communicating with the backend
 */

import axios from 'axios';
import type { DashboardData, KPIMetrics, MetricsResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication (if needed)
api.interceptors.request.use(
  (config) => {
    // Add user headers if available (for demo purposes)
    config.headers['X-User-ID'] = 'demo_user';
    config.headers['X-User-Role'] = 'admin';
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const metricsApi = {
  /**
   * Get all dashboard data in a single request
   */
  getDashboardData: async (): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/api/metrics/dashboard');
    return response.data;
  },

  /**
   * Get KPI metrics
   */
  getKPIs: async (): Promise<KPIMetrics> => {
    const response = await api.get<KPIMetrics>('/api/metrics/kpis');
    return response.data;
  },

  /**
   * Get recent requests
   */
  getRecentRequests: async (params?: {
    limit?: number;
    status?: string;
    model?: string;
  }): Promise<MetricsResponse[]> => {
    const response = await api.get<MetricsResponse[]>('/api/metrics/recent-requests', {
      params,
    });
    return response.data;
  },

  /**
   * Get available models
   */
  getModels: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/api/metrics/models');
    return response.data;
  },

  /**
   * Get available user roles
   */
  getUserRoles: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/api/metrics/user-roles');
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
