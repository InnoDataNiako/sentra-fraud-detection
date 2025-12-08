/**
 * Types TypeScript pour la détection de fraude SÉNTRA
 * Correspondent exactement aux réponses de l'API backend
 */

// ============================================================================
// TYPES DE BASE
// ============================================================================

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type TransactionStatus = 'pending' | 'approved' | 'rejected' | 'fraud';

// ============================================================================
// TRANSACTION (Backend)
// ============================================================================

export interface Transaction {
  id: number;
  transaction_id: string;
  amount: number;
  currency: string;
  transaction_type: string;
  customer_id: string;
  merchant_id: string;
  location: string;
  ip_address: string;
  timestamp: string;
  is_fraud: boolean;
  fraud_score: number;
  fraud_reason?: string;
  status: TransactionStatus;
  created_at?: string;
  updated_at?: string;
}

// export interface TransactionRequest {
//   transaction_id: string;
//   amount: number;
//   currency: string;
//   transaction_type: string;
//   customer_id: string;
//   merchant_id?: string;
//   location?: string;
//   ip_address?: string;
//   timestamp?: string;
//   device_id?: string;  

// }

export interface TransactionRequest {
  transaction_id: string;
  amount: number;
  currency: string;
  transaction_type: string;
  customer_id: string;
  
  // Champs optionnels
  merchant_id?: string;
  location?: string;
  ip_address?: string;
  timestamp?: string;
  device_id?: string;      // ← AJOUTÉ ICI
  
  // Autres champs optionnels
  card_id?: string;
  account_id?: string;
  session_id?: string;
  user_agent?: string;
}

// ============================================================================
// RÉSULTAT DE DÉTECTION (Backend)
// ============================================================================

export interface FraudExplanation {
  top_features: Record<string, number>;
  fraud_indicators: string[];
  risk_factors: Record<string, any>;
}

export interface DetectionResult {
  is_fraud: boolean;
  fraud_probability: number;
  risk_level: RiskLevel;
  confidence_score: number;
  should_block: boolean;
  explanation: FraudExplanation;
}

// ============================================================================
// ALERTE (Backend)
// ============================================================================

export interface FraudAlert {
  id: number;
  alert_id: string;
  transaction_id: number;
  severity: RiskLevel;
  title: string;
  description: string;
  fraud_indicators: string;
  is_reviewed: boolean;
  reviewed_by?: string;
  reviewed_at?: string;
  resolution?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// MÉTRIQUES (Backend)
// ============================================================================

export interface Metrics {
  total_transactions: number;
  frauds_detected: number;
  fraud_rate: number;
  blocked_amount: number;
  avg_processing_time_ms: number;
  model_accuracy: number;
}

export interface AlertMetrics {
  total_alerts: number;
  by_severity: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  resolved_alerts: number;
  pending_alerts: number;
}

// ============================================================================
// RÉPONSES API
// ============================================================================

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// FILTRES
// ============================================================================

export interface TransactionFilters {
  start_date?: string;
  end_date?: string;
  risk_level?: RiskLevel;
  status?: TransactionStatus;
  min_amount?: number;
  max_amount?: number;
  customer_id?: string;
  is_fraud?: boolean;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}