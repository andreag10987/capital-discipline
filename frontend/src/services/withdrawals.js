import api from './api';

export const withdrawalsService = {
  // Crear retiro
  createWithdrawal: async (withdrawalData) => {
    const response = await api.post('/withdrawals/', withdrawalData);
    return response.data;
  },

  // Obtener lista de retiros
  getWithdrawals: async (goalId = null, limit = 100) => {
    const params = {};
    if (goalId) params.goal_id = goalId;
    if (limit) params.limit = limit;
    
    const response = await api.get('/withdrawals/', { params });
    return response.data;
  },

  // Obtener retiro específico
  getWithdrawal: async (withdrawalId) => {
    const response = await api.get(`/withdrawals/${withdrawalId}`);
    return response.data;
  },

  // Eliminar retiro
  deleteWithdrawal: async (withdrawalId) => {
    const response = await api.delete(`/withdrawals/${withdrawalId}`);
    return response.data;
  },
};

export default withdrawalsService;