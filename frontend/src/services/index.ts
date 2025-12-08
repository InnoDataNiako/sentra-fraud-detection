/**
 * Export centralisé de tous les services
 * Facilite les imports : import { detectFraud, getDashboardMetrics } from '@/services'
 */

// Service de détection de fraude
export * from './fraudService';

// Service de métriques
export * from './metricsService';

// Export centralisé des services
export * from './api';
export { default as api } from './api';