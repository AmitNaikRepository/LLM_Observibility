/**
 * Custom hooks for dashboard data fetching
 */

import { useQuery } from '@tanstack/react-query';
import { metricsApi } from '../services/api';

/**
 * Hook to fetch dashboard data
 */
export const useDashboardData = (refetchInterval: number = 5000) => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: metricsApi.getDashboardData,
    refetchInterval,
    staleTime: 4000,
  });
};

/**
 * Hook to fetch KPI metrics
 */
export const useKPIs = (refetchInterval: number = 5000) => {
  return useQuery({
    queryKey: ['kpis'],
    queryFn: metricsApi.getKPIs,
    refetchInterval,
    staleTime: 4000,
  });
};

/**
 * Hook to fetch recent requests
 */
export const useRecentRequests = (
  params?: { limit?: number; status?: string; model?: string },
  refetchInterval: number = 5000
) => {
  return useQuery({
    queryKey: ['recent-requests', params],
    queryFn: () => metricsApi.getRecentRequests(params),
    refetchInterval,
    staleTime: 4000,
  });
};

/**
 * Hook to fetch available models
 */
export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: metricsApi.getModels,
    staleTime: 300000, // 5 minutes
  });
};

/**
 * Hook to fetch available user roles
 */
export const useUserRoles = () => {
  return useQuery({
    queryKey: ['user-roles'],
    queryFn: metricsApi.getUserRoles,
    staleTime: 300000, // 5 minutes
  });
};
