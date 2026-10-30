export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
  };
}

export interface HealthResponse {
  status: 'ok';
  phase: number;
  version: string;
  ai_configured: boolean;
  configured_model: string;
  fallback_model: string | null;
  max_sequence_length_bp: number;
}

export interface BaseCounts {
  A: number;
  T: number;
  G: number;
  C: number;
  N: number;
}

export interface GcWindowPoint {
  position: number;
  gc_percent: number;
}

export interface FastaRecordMeta {
  id: string;
  description: string;
  length: number;
}

export interface AnalyzeRequest {
  sequence_id?: string | null;
  sequence: string;
  include_complements?: boolean;
  gc_window_size?: number;
}

export interface AnalyzeResponse {
  id: string;
  description: string;
  length: number;
  counts: BaseCounts;
  gc_percent: number;
  at_percent: number;
  molecular_weight_da: number;
  molecular_weight_note: string;
  gc_profile: GcWindowPoint[];
  records: FastaRecordMeta[];
  sequence: string;
  complement: string | null;
  reverse_complement: string | null;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) {
    const err = (await response.json()) as ApiErrorEnvelope;
    throw new Error(err.error?.message ?? 'Backend health check failed');
  }
  return (await response.json()) as HealthResponse;
}

export async function postAnalyze(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const err = (await response.json()) as ApiErrorEnvelope;
    throw new Error(err.error?.message ?? 'Sequence analysis failed');
  }
  return (await response.json()) as AnalyzeResponse;
}
