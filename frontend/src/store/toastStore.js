import { create } from 'zustand'

export const useToastStore = create((set) => ({
  toasts: [],

  // Función principal (la que ya tenías)
  addToast: (message, type = 'info') => {
    const id = Date.now()
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }]
    }))

    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((toast) => toast.id !== id)
      }))
    }, 5000)
  },

  // ✅ Alias para compatibilidad con el resto del código
  showToast: (message, type = 'info') => {
    const id = Date.now()
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }]
    }))

    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((toast) => toast.id !== id)
      }))
    }, 5000)
  },

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id)
    }))
}))
