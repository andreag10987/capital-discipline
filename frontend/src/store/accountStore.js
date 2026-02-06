import { create } from 'zustand'
import { getAccount } from '../services/account'

export const useAccountStore = create((set) => ({
  account: null,
  loading: false,

  fetchAccount: async () => {
    set({ loading: true })
    try {
      const data = await getAccount()
      set({ account: data, loading: false })
    } catch (error) {
      console.error('Error fetching account:', error)
      set({ loading: false })
    }
  },

  setAccount: (account) => set({ account }),
  clearAccount: () => set({ account: null })
}))