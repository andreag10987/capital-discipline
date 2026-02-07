/**
 * Servicio de API para endpoints de admin
 */

import api from './api';

/**
 * Obtener métricas del sistema
 */
export const getSystemMetrics = async () => {
  const response = await api.get('/admin/metrics');
  return response.data;
};

/**
 * Listar usuarios con filtros
 */
export const listUsers = async (params = {}) => {
  const { skip = 0, limit = 50, plan = null, is_blocked = null } = params;
  
  const queryParams = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  
  if (plan) queryParams.append('plan', plan);
  if (is_blocked !== null) queryParams.append('is_blocked', is_blocked.toString());
  
  const response = await api.get(`/admin/users?${queryParams.toString()}`);
  return response.data;
};

/**
 * Obtener detalle de usuario
 */
export const getUserDetail = async (userId) => {
  const response = await api.get(`/admin/users/${userId}`);
  return response.data;
};

/**
 * Bloquear usuario
 */
export const blockUser = async (userId, reason) => {
  const response = await api.post(`/admin/users/${userId}/block`, { reason });
  return response.data;
};

/**
 * Desbloquear usuario
 */
export const unblockUser = async (userId) => {
  const response = await api.post(`/admin/users/${userId}/unblock`);
  return response.data;
};

/**
 * Cambiar plan de usuario
 */
export const changeUserPlan = async (userId, planName) => {
  const response = await api.patch(`/admin/users/${userId}/plan`, { plan_name: planName });
  return response.data;
};