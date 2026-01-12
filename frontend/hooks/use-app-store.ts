import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { useCallback, useEffect, useState } from 'react';
import { 
  ProcessingState, 
  ContentRepurposingResult, 
  ProcessingConfig, 
  BrandVoice,
  DashboardMetrics 
} from '@/types';

interface AppState {
  // Processing state
  processing: ProcessingState;
  
  // Configuration
  config: ProcessingConfig;
  
  // Results history
  resultsHistory: ContentRepurposingResult[];
  
  // UI state
  sidebarOpen: boolean;
  darkMode: boolean;
  
  // Dashboard metrics
  metrics: DashboardMetrics;
  
  // Actions
  setProcessing: (processing: Partial<ProcessingState>) => void;
  setConfig: (config: Partial<ProcessingConfig>) => void;
  addResult: (result: ContentRepurposingResult) => void;
  clearResults: () => void;
  toggleSidebar: () => void;
  toggleDarkMode: () => void;
  setMetrics: (metrics: Partial<DashboardMetrics>) => void;
  resetProcessing: () => void;
}

const defaultConfig: ProcessingConfig = {
  brand_voice: BrandVoice.PROFESSIONAL,
  keywords: ['AI', 'machine learning', 'technology'],
  enable_critique: true,
  track_costs: true,
};

const defaultProcessing: ProcessingState = {
  isProcessing: false,
  progress: 0,
  currentStep: '',
};

const defaultMetrics: DashboardMetrics = {
  totalPlatforms: 6,
  totalAgents: 8,
  totalBrandVoices: 5,
  totalQualityChecks: 3,
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      processing: defaultProcessing,
      config: defaultConfig,
      resultsHistory: [],
      sidebarOpen: true,
      darkMode: false,
      metrics: defaultMetrics,

      // Processing actions
      setProcessing: (newProcessing) =>
        set((state) => ({
          processing: { ...state.processing, ...newProcessing }
        })),

      resetProcessing: () =>
        set(() => ({
          processing: defaultProcessing
        })),

      // Configuration actions
      setConfig: (newConfig) =>
        set((state) => ({
          config: { ...state.config, ...newConfig }
        })),

      // Results actions
      addResult: (result) =>
        set((state) => ({
          resultsHistory: [result, ...state.resultsHistory.slice(0, 9)] // Keep last 10 results
        })),

      clearResults: () =>
        set(() => ({
          resultsHistory: []
        })),

      // UI actions
      toggleSidebar: () =>
        set((state) => ({
          sidebarOpen: !state.sidebarOpen
        })),

      toggleDarkMode: () =>
        set((state) => {
          const newDarkMode = !state.darkMode;
          return { darkMode: newDarkMode };
        }),

      // Metrics actions
      setMetrics: (newMetrics) =>
        set((state) => ({
          metrics: { ...state.metrics, ...newMetrics }
        })),
    }),
    {
      name: 'content-repurposer-storage',
      partialize: (state) => ({
        config: state.config,
        sidebarOpen: state.sidebarOpen,
        darkMode: state.darkMode,
        resultsHistory: state.resultsHistory.slice(0, 5), // Persist only last 5 results
      }),
      storage: typeof window !== 'undefined' ? {
        getItem: (name) => {
          const item = localStorage.getItem(name);
          return item ? JSON.parse(item) : null;
        },
        setItem: (name, value) => {
          localStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name) => {
          localStorage.removeItem(name);
        },
      } : undefined,
    }
  )
);

// Selectors for easier access
export const useProcessing = () => useAppStore((state) => state.processing);
export const useConfig = () => useAppStore((state) => state.config);
export const useResultsHistory = () => useAppStore((state) => state.resultsHistory);

// Individual UI selectors to prevent infinite loops
export const useSidebarOpen = () => useAppStore((state) => state.sidebarOpen);
export const useDarkMode = () => useAppStore((state) => state.darkMode);

// Combined UI hook with stable references
export const useUI = () => {
  const sidebarOpen = useSidebarOpen();
  const darkMode = useDarkMode();
  const store = useAppStore();
  
  return {
    sidebarOpen,
    darkMode,
    toggleSidebar: store.toggleSidebar,
    toggleDarkMode: store.toggleDarkMode,
  };
};

export const useMetrics = () => useAppStore((state) => state.metrics);

// Actions hook with stable references
export const useAppActions = () => {
  const store = useAppStore();
  
  return {
    setProcessing: store.setProcessing,
    setConfig: store.setConfig,
    addResult: store.addResult,
    clearResults: store.clearResults,
    toggleSidebar: store.toggleSidebar,
    toggleDarkMode: store.toggleDarkMode,
    setMetrics: store.setMetrics,
    resetProcessing: store.resetProcessing,
  };
};

// Initialize dark mode from persisted state - moved to separate hook
export const useDarkModeInitialization = () => {
  const [isClient, setIsClient] = useState(false);
  const darkMode = useDarkMode();
  
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  useEffect(() => {
    if (isClient && typeof window !== 'undefined') {
      if (darkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  }, [darkMode, isClient]);
};
