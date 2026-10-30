import { create } from 'zustand';
import { AnalyzeResponse, HealthResponse } from '../lib/api';

export interface GenomeStoreState {
  phase: number;
  health: HealthResponse | null;
  healthStatus: 'idle' | 'loading' | 'connected' | 'error';
  healthError: string | null;
  rawInputText: string;
  analysis: AnalyzeResponse | null;
  analyzeStatus: 'idle' | 'loading' | 'ready' | 'error';
  analyzeError: string | null;
  setHealth: (health: HealthResponse) => void;
  setHealthStatus: (status: 'idle' | 'loading' | 'connected' | 'error', error?: string | null) => void;
  setRawInputText: (rawInputText: string) => void;
  setAnalysis: (analysis: AnalyzeResponse) => void;
  setAnalyzeStatus: (status: 'idle' | 'loading' | 'ready' | 'error', error?: string | null) => void;
}

export const useGenomeStore = create<GenomeStoreState>((set) => ({
  phase: 2,
  health: null,
  healthStatus: 'idle',
  healthError: null,
  rawInputText: '',
  analysis: null,
  analyzeStatus: 'idle',
  analyzeError: null,
  setHealth: (health) => set({ health, healthStatus: 'connected', healthError: null }),
  setHealthStatus: (healthStatus, healthError = null) => set({ healthStatus, healthError }),
  setRawInputText: (rawInputText) => set({ rawInputText }),
  setAnalysis: (analysis) => set({ analysis, analyzeStatus: 'ready', analyzeError: null }),
  setAnalyzeStatus: (analyzeStatus, analyzeError = null) => set({ analyzeStatus, analyzeError }),
}));
