import api from './api';

export const goalsService = {
  // Crear objetivo
  createGoal: async (goalData) => {
    const response = await api.post('/goals/', goalData);
    return response.data;
  },

  // Obtener todos los objetivos
  getGoals: async () => {
    const response = await api.get('/goals/');
    return response.data;
  },

  // Obtener objetivo específico
  getGoal: async (goalId) => {
    const response = await api.get(`/goals/${goalId}`);
    return response.data;
  },

  // Actualizar objetivo
  updateGoal: async (goalId, goalData) => {
    const response = await api.put(`/goals/${goalId}`, goalData);
    return response.data;
  },

  // Eliminar objetivo
  deleteGoal: async (goalId) => {
    const response = await api.delete(`/goals/${goalId}`);
    return response.data;
  },

  // Obtener progreso del objetivo
  getGoalProgress: async (goalId) => {
    const response = await api.get(`/goals/${goalId}/progress`);
    return response.data;
  },

  // Obtener calendario del objetivo
  getGoalCalendar: async (goalId, rangeRequest = null) => {
    const response = await api.post(`/goals/${goalId}/calendar`, rangeRequest || {});
    return response.data;
  },
};

export default goalsService;