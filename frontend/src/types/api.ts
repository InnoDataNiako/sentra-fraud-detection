/**
 * Types TypeScript pour les réponses API
 */

// ============================================================================
// RÉPONSES API GÉNÉRIQUES
// ============================================================================

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  status?: number;
  timestamp?: string;
}

export interface ApiError {
  error: string;
  message?: string;
  details?: string | string[];
  status_code: number;
  path?: string;
  timestamp: string;
  request_id?: string;
}

// ============================================================================
// HEALTH CHECK
// ============================================================================

export interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded';
  service: string;
  version?: string;
  timestamp?: string;
}

export interface DetailedStatus {
  status: 'operational' | 'degraded' | 'down';
  service: string;
  version: string;
  environment: string;
  uptime: string;
  components: {
    api: 'healthy' | 'unhealthy';
    database: 'connected' | 'disconnected';
    ml_model: 'loaded' | 'unloaded';
    cache: 'active' | 'inactive';
  };
  security: {
    rate_limiting: 'enabled' | 'disabled';
    cors: 'configured' | 'unconfigured';
    headers: 'secured' | 'unsecured';
  };
  timestamp: string;
}

// ============================================================================
// ÉTATS DE CHARGEMENT
// ============================================================================

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// ============================================================================
// RÉPONSES SPÉCIFIQUES
// ============================================================================

export interface BatchDetectionResponse {
  results: any[]; // Remplacer par DetectionResult[] si importé
  total_processed: number;
  successful: number;
  failed: number;
  processing_time_ms: number;
}

export interface DailyReportResponse {
  date: string;
  summary: {
    total_transactions: number;
    fraud_detected: number;
    fraud_rate: number;
    total_amount: number;
    blocked_amount: number;
  };
  top_fraud_types: Array<{
    type: string;
    count: number;
  }>;
  hourly_distribution: Array<{
    hour: number;
    transactions: number;
    frauds: number;
  }>;
  generated_at: string;
}

// ============================================================================
// MESSAGES DE TOAST/NOTIFICATION
// ============================================================================

export interface ToastMessage {
  id?: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}