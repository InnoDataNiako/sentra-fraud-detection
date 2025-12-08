/**
 * Service pour les statistiques et analytics
 * Communique avec l'API backend /stats
 */

import api from '@/api';

export interface DashboardData {
  summary: {
    summary: {
      total_transactions: number;
      fraud_transactions: number;
      fraud_rate: number;
      total_amount: number;
      avg_amount: number;
      min_amount: number;
      max_amount: number;
      avg_fraud_score: number;
      last_24h: {
        transactions: number;
        frauds: number;
        fraud_rate: number;
      };
    };
    amount_distribution: Array<{
      range: string;
      count: number;
      fraud_count: number;
    }>;
    timestamp: string;
  };
  trends: {
    period_days: number;
    daily_data: Array<{
      date: string;
      total: number;
      fraud: number;
      fraud_rate: number;
      avg_fraud_score: number;
      total_amount: number;
    }>;
    total_days: number;
  };
  by_type: {
    by_type: Array<{
      type: string;
      total: number;
      fraud: number;
      fraud_rate: number;
      avg_amount: number;
      avg_fraud_score: number;
    }>;
  };
  score_distribution: {
    distribution: Array<{
      level: string;
      count: number;
      avg_score: number;
      color: string;
    }>;
  };
  top_stats: {
    top_fraudulent_clients: Array<{
      customer_id: string;
      total_transactions: number;
      fraud_count: number;
      fraud_rate: number;
    }>;
    top_fraud_transactions: Array<{
      transaction_id: string;
      customer_id: string;
      amount: number;
      fraud_score: number;
      created_at: string;
    }>;
  };
  generated_at: string;
  total_transactions_in_db: number;
}

export interface SummaryStats {
  summary: {
    total_transactions: number;
    fraud_transactions: number;
    fraud_rate: number;
    total_amount: number;
    avg_amount: number;
    min_amount: number;
    max_amount: number;
    avg_fraud_score: number;
    last_24h: {
      transactions: number;
      frauds: number;
      fraud_rate: number;
    };
  };
  amount_distribution: Array<{
    range: string;
    count: number;
    fraud_count: number;
  }>;
  timestamp: string;
}

export interface DailyTrend {
  period_days: number;
  daily_data: Array<{
    date: string;
    total: number;
    fraud: number;
    fraud_rate: number;
    avg_fraud_score: number;
    total_amount: number;
  }>;
  total_days: number;
}

export interface StatsByType {
  by_type: Array<{
    type: string;
    total: number;
    fraud: number;
    fraud_rate: number;
    avg_amount: number;
    avg_fraud_score: number;
  }>;
}

export interface ScoreDistribution {
  distribution: Array<{
    level: string;
    count: number;
    avg_score: number;
    color: string;
  }>;
}

export interface TopStats {
  top_fraudulent_clients: Array<{
    customer_id: string;
    total_transactions: number;
    fraud_count: number;
    fraud_rate: number;
  }>;
  top_fraud_transactions: Array<{
    transaction_id: string;
    customer_id: string;
    amount: number;
    fraud_score: number;
    created_at: string;
  }>;
}

class StatsService {
  /**
   * Récupère TOUTES les données du dashboard en un seul appel
   * Endpoint optimisé qui combine toutes les statistiques
   */
  async getDashboardData(): Promise<DashboardData> {
    try {
      const response = await api.get<DashboardData>('/stats/dashboard');
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors du chargement du dashboard:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossible de charger les données du dashboard'
      );
    }
  }

  /**
   * Récupère uniquement le résumé des statistiques globales
   */
  async getSummary(): Promise<SummaryStats> {
    try {
      const response = await api.get<SummaryStats>('/stats/summary');
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors du chargement du résumé:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossible de charger le résumé'
      );
    }
  }

  /**
   * Récupère les tendances quotidiennes
   * @param days Nombre de jours (1-90)
   */
  async getDailyTrend(days: number = 30): Promise<DailyTrend> {
    try {
      const response = await api.get<DailyTrend>('/stats/trend/daily', {
        params: { days }
      });
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors du chargement des tendances:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossible de charger les tendances'
      );
    }
  }

  /**
   * Récupère les statistiques par type de transaction
   */
  async getStatsByType(): Promise<StatsByType> {
    try {
      const response = await api.get<StatsByType>('/stats/by-type');
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors du chargement des stats par type:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossible de charger les stats par type'
      );
    }
  }

  /**
   * Récupère la distribution des scores de fraude
   */
  async getScoreDistribution(): Promise<ScoreDistribution> {
    try {
      const response = await api.get<ScoreDistribution>('/stats/score-distribution');
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors du chargement de la distribution:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossible de charger la distribution des scores'
      );
    }
  }

  /**
   * Récupère les top statistiques (clients frauduleux, transactions)
   * @param limit Nombre d'éléments (1-50)
   */
  async getTopStats(limit: number = 10): Promise<TopStats> {
    try {
      const response = await api.get<TopStats>('/stats/top', {
        params: { limit }
      });
      return response.data;
    } catch (error: any) {
      console.error('❌ Erreur lors du chargement du top stats:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossible de charger le top stats'
      );
    }
  }

  /**
   * Exporte les données du dashboard en JSON
   */
  async exportDashboardData(data: DashboardData): Promise<void> {
    try {
      const exportData = {
        exported_at: new Date().toISOString(),
        ...data
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sentra-analytics-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('❌ Erreur lors de l\'export:', error);
      throw new Error('Impossible d\'exporter les données');
    }
  }

  /**
   * Exporte les données en CSV
   */
  async exportToCSV(data: DashboardData): Promise<void> {
    try {
      // Préparer les données pour CSV
      const csvRows = [];
      
      // En-têtes
      csvRows.push([
        'Date',
        'Total Transactions',
        'Fraudes',
        'Taux de Fraude (%)',
        'Montant Total',
        'Score Moyen'
      ].join(','));

      // Données quotidiennes
      data.trends.daily_data.forEach(day => {
        csvRows.push([
          day.date,
          day.total,
          day.fraud,
          day.fraud_rate.toFixed(2),
          day.total_amount,
          day.avg_fraud_score.toFixed(2)
        ].join(','));
      });

      // Créer le blob et télécharger
      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sentra-analytics-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('❌ Erreur lors de l\'export CSV:', error);
      throw new Error('Impossible d\'exporter en CSV');
    }
  }
}

// Export de l'instance unique
export const statsService = new StatsService();

// Export des types pour utilisation ailleurs
export type {
  DashboardData,
  SummaryStats,
  DailyTrend,
  StatsByType,
  ScoreDistribution,
  TopStats
};