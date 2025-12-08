/**
 * Service de métriques et analytics
 * Gère tous les appels API liés aux statistiques
 */

import api, { apiCall } from '@/lib/api';
import {
  DashboardMetrics,
  AlertMetrics,
  ModelMetrics,
  PerformanceMetrics,
  ChartDataPoint,
  AmountDistribution,
  HealthCheck,
  DetailedStatus,
} from '@/types';

// ============================================================================
// HEALTH & STATUS
// ============================================================================

/**
 * Vérifie la santé du système
 */
export async function getHealth(): Promise<HealthCheck> {
  return apiCall(() => api.get<HealthCheck>('/health'));
}

/**
 * Récupère le statut détaillé du système
 */
export async function getDetailedStatus(): Promise<DetailedStatus> {
  return apiCall(() => api.get<DetailedStatus>('/status'));
}

// ============================================================================
// MÉTRIQUES DASHBOARD
// ============================================================================

/**
 * Récupère les métriques du tableau de bord
 */
export async function getDashboardMetrics(
  period?: string
): Promise<DashboardMetrics> {
  const query = period ? `?period=${period}` : '';
  return apiCall(() => api.get<DashboardMetrics>(`/metrics/dashboard${query}`));
}

/**
 * Récupère les statistiques des alertes
 */
export async function getAlertMetrics(): Promise<AlertMetrics> {
  return apiCall(() => api.get<AlertMetrics>('/metrics/alerts'));
}

/**
 * Récupère les métriques du modèle ML
 */
export async function getModelMetrics(): Promise<ModelMetrics> {
  return apiCall(() => api.get<ModelMetrics>('/metrics/model'));
}

/**
 * Récupère les métriques de performance système
 */
export async function getPerformanceMetrics(): Promise<PerformanceMetrics> {
  return apiCall(() => api.get<PerformanceMetrics>('/metrics/performance'));
}

// ============================================================================
// RAPPORTS & ANALYTICS
// ============================================================================

/**
 * Récupère le rapport quotidien
 */
export async function getDailyReport(date?: string): Promise<any> {
  const query = date ? `?date=${date}` : '';
  return apiCall(() => api.get(`/metrics/daily-report${query}`));
}

/**
 * Récupère les données pour graphique d'évolution
 */
export async function getFraudTrendData(
  startDate?: string,
  endDate?: string
): Promise<ChartDataPoint[]> {
  // Note: Endpoint à confirmer avec backend
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  const query = params.toString();
  return apiCall(() =>
    api.get<ChartDataPoint[]>(`/metrics/fraud-trend${query ? `?${query}` : ''}`)
  );
}

/**
 * Récupère la distribution des montants
 */
export async function getAmountDistribution(): Promise<AmountDistribution[]> {
  // Note: Endpoint à confirmer avec backend
  return apiCall(() =>
    api.get<AmountDistribution[]>('/metrics/amount-distribution')
  );
}

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Calcule le taux de variation entre deux valeurs
 */
export function calculateChangeRate(
  current: number,
  previous: number
): number {
  if (previous === 0) return current > 0 ? 100 : 0;
  return ((current - previous) / previous) * 100;
}

/**
 * Formate un pourcentage
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Détermine la couleur selon le taux de fraude
 */
export function getFraudRateColor(rate: number): string {
  if (rate < 2) return 'green';
  if (rate < 5) return 'yellow';
  if (rate < 10) return 'orange';
  return 'red';
}

/**
 * Génère des données mock pour développement (à supprimer en production)
 */
export function generateMockChartData(days: number = 7): ChartDataPoint[] {
  const data: ChartDataPoint[] = [];
  const today = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    const transactions = Math.floor(Math.random() * 500) + 200;
    const frauds = Math.floor(Math.random() * 20) + 5;

    data.push({
      date: date.toISOString().split('T')[0],
      transactions,
      frauds,
      fraud_rate: (frauds / transactions) * 100,
    });
  }

  return data;
}