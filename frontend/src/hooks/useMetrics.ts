/**
 * Hook personnalisé pour récupérer les métriques
 * 🔧 VERSION CORRIGÉE - Utilise les vraies données de l'API
 */
import { useState, useEffect } from 'react';
import { getDashboardMetrics } from '@/services';
import { DashboardMetrics } from '@/types';

interface UseMetricsResult {
  metrics: DashboardMetrics | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

// Interface pour la réponse imbriquée de l'API
interface NestedApiResponse {
  timestamp: string;
  time_periods: {
    last_24h: string;
    last_7d: string;
  };
  transactions: {
    total_transactions: number;
    total_revenue: number;
    last_24h_detail: {
      total: number;
      fraudulent: number;
      fraud_rate: number;
      total_amount: number;
      avg_amount: number;
    };
    last_7d_detail: {
      total_transactions: number;
      fraudulent_transactions: number;
      fraud_rate: number;
      total_amount: number;
      average_fraud_score: number;
    };
  };
  alerts: {
    frauds_detected: number;
    fraud_rate: number;
    blocked_amount: number;
    total: number;
    unreviewed: number;
    distribution: {
      critical: number;
      high: number;
      medium: number;
      low: number;
    };
    review_rate: number;
  };
  performance: {
    model_accuracy: number;
    avg_processing_time_ms: number;
    detection_accuracy: number;
    false_positive_rate: number;
    auto_block_rate: number;
  };
}

/**
 * 🔧 CORRECTION MAJEURE : Utilise les données à la racine au lieu de last_7d_detail
 * Le backend retourne les données dans transactions.total_transactions et alerts.frauds_detected
 */
function flattenMetrics(nestedData: NestedApiResponse): DashboardMetrics {
  console.log('🔍 Données reçues de l\'API:', nestedData);
  
  // 🔧 UTILISER LES DONNÉES À LA RACINE (transactions.total_transactions)
  const flatMetrics: DashboardMetrics = {
    // Métriques de Transactions - Utiliser la racine
    total_transactions: nestedData.transactions.total_transactions,
    total_revenue: nestedData.transactions.total_revenue,
    
    // Métriques d'Alertes - Utiliser alerts à la racine
    frauds_detected: nestedData.alerts.frauds_detected,
    blocked_amount: nestedData.alerts.blocked_amount,
    fraud_rate: nestedData.alerts.fraud_rate,
    
    // Métriques de Performance
    model_accuracy: nestedData.performance.model_accuracy,
    avg_processing_time_ms: nestedData.performance.avg_processing_time_ms,
    
    // Champs secondaires
    timestamp: nestedData.timestamp,
  };
  
  console.log('✅ Métriques finales calculées:', flatMetrics);
  
  return flatMetrics;
}

export function useMetrics(): UseMetricsResult {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const nestedData = await getDashboardMetrics();
      
      console.log("✅ Données métriques brutes reçues (imbriquées - API):", nestedData);
      
      const flatMetrics = flattenMetrics(nestedData as NestedApiResponse);
      console.log("🛠️ Données métriques transformées (plates - Frontend):", flatMetrics);
      
      setMetrics(flatMetrics);
    } catch (err: any) {
      console.error('❌ Erreur lors de la récupération des métriques:', err);
      setError(err.message || 'Erreur lors du chargement des métriques.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return {
    metrics,
    loading,
    error,
    refresh: fetchMetrics,
  };
}