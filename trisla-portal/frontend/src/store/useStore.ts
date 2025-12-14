import { create } from 'zustand'
import { Module, HealthGlobal, Intent, Contract, Trace, SLO } from '@/types'

interface AppState {
  // Health
  health: HealthGlobal | null
  modules: Module[]
  loading: boolean
  error: string | null

  // Actions
  setHealth: (health: HealthGlobal) => void
  setModules: (modules: Module[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  fetchHealth: () => Promise<void>
  fetchModules: () => Promise<void>
}

export const useStore = create<AppState>((set) => ({
  health: null,
  modules: [],
  loading: false,
  error: null,

  setHealth: (health) => set({ health }),
  setModules: (modules) => set({ modules }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  fetchHealth: async () => {
    set({ loading: true, error: null })
    try {
      const { apiClient } = await import('@/lib/api')
      const health = await apiClient.getHealthGlobal()
      set({ health, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  fetchModules: async () => {
    set({ loading: true, error: null })
    try {
      const { apiClient } = await import('@/lib/api')
      const modules = await apiClient.getModules()
      set({ modules, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },
}))







