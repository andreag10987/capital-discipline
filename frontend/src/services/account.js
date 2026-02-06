import api from './api'

export const createAccount = async (capital, payout) => {
  const response = await api.post('/account', { capital, payout })
  return response.data
}

export const getAccount = async () => {
  const response = await api.get('/account')
  return response.data
}

export const updateAccount = async (data) => {
  const response = await api.put('/account', data)
  return response.data
}