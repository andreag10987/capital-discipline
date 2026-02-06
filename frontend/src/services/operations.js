import api from './api'

export const createOperation = async (data) => {
  const response = await api.post('/operations', data)
  return response.data
}

export const getOperations = async (sessionId) => {
  const response = await api.get('/operations', { params: { session_id: sessionId } })
  return response.data
}