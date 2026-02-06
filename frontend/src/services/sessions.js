import api from './api'

export const createSession = async (risk_percent) => {
  const response = await api.post('/sessions', { risk_percent })
  return response.data
}

export const getSessions = async () => {
  const response = await api.get('/sessions')
  return response.data
}