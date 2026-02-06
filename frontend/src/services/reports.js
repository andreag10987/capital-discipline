import api from './api'

export const getReports = async (days) => {
  const response = await api.get('/reports', { params: { days } })
  return response.data
}

export const getProjections = async (days) => {
  const response = await api.get('/projections', { params: { days } })
  return response.data
}