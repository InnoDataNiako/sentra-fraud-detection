import { api } from '../lib/api';
import {
  Transaction,
  TransactionRequest,
  DetectionResult,
  Metrics,
  FraudAlert,
  TransactionFilters,
  PaginationParams,
  PaginatedResponse
} from '@/types/fraud';

// ==========================================================================
// NOUVELLES INTERFACES POUR LA GESTION DES CLIENTS
// ==========================================================================

export interface Customer {
  customer_id: string;
  transaction_count: number;
  last_transaction: string | null;
  avg_amount: number;
  fraud_count: number;
  fraud_rate: number;
}

export interface CustomerStats {
  customer_id: string;
  period_days: number;
  transaction_count: number;
  total_amount: number;
  avg_amount: number;
  min_amount: number;
  max_amount: number;
  fraud_count: number;
  fraud_rate: number;
  last_transaction: string;
  first_transaction: string;
  common_location: string;
  common_type: string;
  locations: string[];
  has_fraud_history: boolean;
}

export interface CustomerTransaction {
  transaction_id: string;
  amount: number;
  currency: string;
  location: string | null;
  timestamp: string;
  is_fraud: boolean;
  fraud_score: number;
}

// ==========================================================================
// SERVICE PRINCIPAL
// ==========================================================================

export const fraudService = {
  // ==========================================================================
  // DÉTECTION DE FRAUDE
  // ==========================================================================

  /**
   * Détecte une fraude pour une transaction unique
   */
  detectFraud: async (transaction: TransactionRequest): Promise<DetectionResult> => {
    const response = await api.post<DetectionResult>('/detect', transaction);
    return response.data;
  },

  /**
   * Détection de fraude par lot (batch)
   */
  detectFraudBatch: async (transactions: TransactionRequest[]): Promise<{ results: DetectionResult[]; total_processed: number }> => {
    const response = await api.post('/detect/batch', { transactions });
    return response.data;
  },

  /**
   * Récupère le statut d'une transaction
   */
  getTransactionStatus: async (transactionId: string): Promise<DetectionResult> => {
    const response = await api.get<DetectionResult>(`/detect/status/${transactionId}`);
    return response.data;
  },

  /**
   * Récupère l'historique des détections
   */
  getDetectionHistory: async (params?: { limit?: number; offset?: number }): Promise<DetectionResult[]> => {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const query = queryParams.toString();
    const response = await api.get<DetectionResult[]>(`/detect/history${query ? `?${query}` : ''}`);
    return response.data;
  },

  // ==========================================================================
  // GESTION DES TRANSACTIONS
  // ==========================================================================

  /**
   * Récupère la liste des transactions avec filtres
   */
  getTransactions: async (
    filters: TransactionFilters = {},
    pagination: PaginationParams = { page_size: 50 }
  ): Promise<PaginatedResponse<Transaction>> => {
    const params = {
      ...filters,
      ...pagination,
    };

    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, String(value));
      }
    });

    const query = queryParams.toString();
    
    const response = await api.get<any>(`/transactions${query ? `?${query}` : ''}`);
    return {
      items: response.data.transactions || [],
      total: response.data.total || 0,
      page: response.data.page || 1,
      page_size: response.data.page_size || pagination.page_size || 50,
      total_pages: response.data.total_pages || 1
    };
  },

  /**
   * Récupère une transaction par ID
   */
  getTransaction: async (id: number): Promise<Transaction> => {
    const response = await api.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },

  /**
   * Crée une nouvelle transaction
   */
  createTransaction: async (transaction: TransactionRequest): Promise<Transaction> => {
    const response = await api.post<Transaction>('/transactions', transaction);
    return response.data;
  },

  /**
   * Met à jour une transaction
   */
  updateTransaction: async (id: number, updates: Partial<Transaction>): Promise<Transaction> => {
    const response = await api.put<Transaction>(`/transactions/${id}`, updates);
    return response.data;
  },

  // ==========================================================================
  // MÉTRIQUES & ANALYTICS
  // ==========================================================================

  /**
   * Récupère les métriques du tableau de bord
   */
  getMetrics: async (): Promise<Metrics> => {
    const response = await api.get<Metrics>('/metrics/dashboard');
    return response.data;
  },

  /**
   * Récupère les statistiques des alertes
   */
  getAlertStats: async (): Promise<any> => {
    const response = await api.get('/metrics/alerts');
    return response.data;
  },

  /**
   * Récupère les métriques du modèle ML
   */
  getModelMetrics: async (): Promise<any> => {
    const response = await api.get('/metrics/model');
    return response.data;
  },

  /**
   * Récupère les performances système
   */
  getPerformanceMetrics: async (): Promise<any> => {
    const response = await api.get('/metrics/performance');
    return response.data;
  },

  /**
   * Récupère les alertes de fraude
   */
  getAlerts: async (params?: { limit?: number; resolved?: boolean }): Promise<FraudAlert[]> => {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.resolved !== undefined) queryParams.append('resolved', params.resolved.toString());

    const query = queryParams.toString();
    const response = await api.get<FraudAlert[]>(`/metrics/alerts${query ? `?${query}` : ''}`);
    return response.data;
  },

  /**
   * Récupère le rapport quotidien
   */
  getDailyReport: async (): Promise<any> => {
    const response = await api.get('/metrics/daily-report');
    return response.data;
  },

  // ==========================================================================
  // SANTÉ DU SYSTÈME
  // ==========================================================================

  /**
   * Vérifie la santé de l'API
   */
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/health');
    return response.data;
  },

  /**
   * Vérifie le statut complet du système
   */
  systemStatus: async (): Promise<any> => {
    const response = await api.get('/status');
    return response.data;
  },

  // ==========================================================================
  // GESTION DES CLIENTS (NOUVELLES MÉTHODES)
  // ==========================================================================

  /**
   * Récupère la liste des clients existants
   */
  getCustomers: async (limit: number = 100): Promise<Customer[]> => {
    try {
      console.log("📡 Récupération des clients depuis l'API...");
      const response = await api.get(`/customers?limit=${limit}&min_transactions=1`);
      const customers = response.data;
      console.log(`✅ ${customers.length} clients récupérés`);
      return customers;
    } catch (error: any) {
      console.error("❌ Erreur récupération clients:", error);
      
      // Données de test pour le développement
      return [
        {
          customer_id: "CUST-12345",
          transaction_count: 15,
          last_transaction: "2025-11-30T10:00:00",
          avg_amount: 45000,
          fraud_count: 0,
          fraud_rate: 0.0
        },
        {
          customer_id: "CUST-67890", 
          transaction_count: 28,
          last_transaction: "2025-11-29T15:30:00",
          avg_amount: 125000,
          fraud_count: 2,
          fraud_rate: 7.1
        },
        {
          customer_id: "CUST-8287",
          transaction_count: 42,
          last_transaction: "2025-11-30T09:45:00",
          avg_amount: 55500,
          fraud_count: 1,
          fraud_rate: 2.4
        },
        {
          customer_id: "CUST-9876",
          transaction_count: 8,
          last_transaction: "2025-11-28T14:20:00",
          avg_amount: 23000,
          fraud_count: 0,
          fraud_rate: 0.0
        }
      ];
    }
  },

  /**
   * Récupère les statistiques détaillées d'un client
   */
  getCustomerStats: async (customerId: string, days: number = 90): Promise<CustomerStats> => {
    try {
      console.log(`📡 Récupération stats client ${customerId}...`);
      const response = await api.get(`/customers/${customerId}/stats?days=${days}`);
      console.log("✅ Stats client récupérées:", response.data);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Erreur stats client ${customerId}:`, error);
      
      // Données de test pour le développement
      return {
        customer_id: customerId,
        period_days: days,
        transaction_count: 15,
        total_amount: 675000,
        avg_amount: 45000,
        min_amount: 10000,
        max_amount: 150000,
        fraud_count: 0,
        fraud_rate: 0.0,
        last_transaction: "2025-11-30T10:00:00",
        first_transaction: "2025-08-15T14:20:00",
        common_location: "Dakar, Sénégal",
        common_type: "payment",
        locations: ["Dakar, Sénégal", "Abidjan, Côte d'Ivoire"],
        has_fraud_history: false
      };
    }
  },

  /**
   * Récupère les dernières transactions d'un client
   */
  getCustomerTransactions: async (customerId: string, limit: number = 5): Promise<CustomerTransaction[]> => {
    try {
      console.log(`📡 Récupération transactions client ${customerId}...`);
      const response = await api.get(`/customers/${customerId}/transactions?limit=${limit}`);
      return response.data;
    } catch (error: any) {
      console.error(`❌ Erreur transactions client ${customerId}:`, error);
      
      // Données de test pour le développement
      return [
        {
          transaction_id: "TXN-20251130-001",
          amount: 45000,
          currency: "XOF",
          location: "Dakar, Sénégal",
          timestamp: "2025-11-30T10:00:00",
          is_fraud: false,
          fraud_score: 0.12
        },
        {
          transaction_id: "TXN-20251129-045",
          amount: 38000,
          currency: "XOF",
          location: "Dakar, Sénégal",
          timestamp: "2025-11-29T15:30:00",
          is_fraud: false,
          fraud_score: 0.08
        }
      ];
    }
  },

  /**
   * Charge toutes les données d'un client (stats + transactions)
   */
  loadCustomerData: async (customerId: string) => {
    try {
      console.log(`📥 Chargement données complètes client ${customerId}...`);
      const [stats, transactions] = await Promise.all([
        fraudService.getCustomerStats(customerId),
        fraudService.getCustomerTransactions(customerId, 3)
      ]);
      
      return {
        stats,
        recentTransactions: transactions
      };
    } catch (error) {
      console.error(`❌ Erreur chargement données client ${customerId}:`, error);
      throw error;
    }
  },

  /**
   * Auto-remplit le formulaire avec les habitudes d'un client
   */
  autoFillFromCustomer: (customerStats: CustomerStats, currentFormData: any) => {
    const suggestions = {
      amount: Math.round(customerStats.avg_amount * 0.8), // 80% du montant moyen
      location: customerStats.common_location || "Dakar, Sénégal",
      transaction_type: customerStats.common_type || "payment",
      currency: "XOF",
      // Suggestions pour les autres champs basées sur l'historique
      suggested_amounts: [
        Math.round(customerStats.avg_amount * 0.5),
        Math.round(customerStats.avg_amount * 0.8),
        Math.round(customerStats.avg_amount * 1.2)
      ],
      risk_level: customerStats.has_fraud_history ? "MEDIUM" : "LOW"
    };
    
    return {
      ...currentFormData,
      ...suggestions,
      customer_id: customerStats.customer_id,
      merchant_id: `MERCH-${customerStats.customer_id.slice(-4)}`
    };
  },

  // ==========================================================================
  // UTILITAIRES
  // ==========================================================================

  /**
   * Génère un ID de transaction unique
   */
  generateTransactionId: (): string => {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 9).toUpperCase();
    return `TXN-${timestamp}-${random}`;
  },

  /**
   * Valide une transaction avant soumission
   */
  validateTransaction: (transaction: TransactionRequest): { valid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (!transaction.transaction_id || transaction.transaction_id.trim() === '') {
      errors.push('ID de transaction requis');
    }

    if (!transaction.amount || transaction.amount <= 0) {
      errors.push('Montant doit être supérieur à 0');
    }

    if (transaction.amount > 10000000) {
      errors.push('Montant trop élevé (max: 10,000,000)');
    }

    if (!transaction.customer_id || transaction.customer_id.trim() === '') {
      errors.push('ID client requis');
    }

    if (!transaction.currency) {
      errors.push('Devise requise');
    }

    if (!transaction.transaction_type) {
      errors.push('Type de transaction requis');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
};