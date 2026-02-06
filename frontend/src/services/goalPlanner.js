import api from './api'

export const createOrUpdateGoal = async (targetCapital) => {
  const response = await api.post('/goal-planner/goal', { target_capital: targetCapital })
  return response.data
}

export const getGoal = async () => {
  const response = await api.get('/goal-planner/goal')
  return response.data
}

export const deleteGoal = async () => {
  const response = await api.delete('/goal-planner/goal')
  return response.data
}

export const calculatePlan = async (planData) => {
  const response = await api.post('/goal-planner/calculate', planData)
  return response.data
}