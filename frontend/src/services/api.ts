import axios from 'axios';

/**
 * Service API pour communiquer avec le backend SÉNTRA
 * Configuration automatique pour Render/Local
 */

// Déterminer l'URL de base automatiquement
const getBaseURL = (): string => {
  // 1. Si en production et sur Render, utiliser l'URL Render
  if (import.meta.env.PROD && import.meta.env.VITE_RENDER === 'true') {
    return import.meta.env.VITE_API_URL || 'https://sentra-backend.onrender.com/api/v1';
  }
  
  // 2. Si en développement avec VITE_API_URL définie
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // 3. Par défaut : localhost
  return 'http://localhost:8000/api/v1';
};

// Création de l'instance axios
export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000, // 30 secondes (important pour Render)
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Intercepteurs pour le logging et gestion d'erreurs
api.interceptors.request.use(
  (config) => {
    // Log en développement
    if (!import.meta.env.PROD) {
      console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    // Ajouter un timestamp pour éviter le cache
    if (config.method?.toLowerCase() === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      };
    }
    
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    // Log en développement
    if (!import.meta.env.PROD) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    // Gestion centralisée des erreurs
    console.error('❌ API Error:', {
      status: error.response?.status,
      message: error.response?.data?.message || error.message,
      url: error.config?.url,
    });
    
    // Erreurs spécifiques
    if (error.response?.status === 401) {
      // Rediriger vers login si besoin
      console.warn('⚠️ Session expirée, redirection nécessaire');
    }
    
    if (error.response?.status === 429) {
      // Rate limiting
      console.warn('⚠️ Trop de requêtes, veuillez patienter');
    }
    
    return Promise.reject(error);
  }
);

// Types pour les requêtes API
export interface Transaction {
  id: string;
  amount: number;
  customer_id: string;
  transaction_type: string;
  location: string;
  timestamp: string;
  fraud_score?: number;
  is_fraud?: boolean;
  status?: string;
}

export interface FraudDetectionRequest {
  transaction_id: string;
  amount: number;
  customer_id: string;
  transaction_type: string;
  location: string;
  device_id?: string;
  timestamp?: string;
}

export interface FraudDetectionResponse {
  transaction_id: string;
  is_fraud: boolean;
  fraud_score: number;
  confidence: number;
  risk_level: 'low' | 'medium' | 'high';
  explanations: Array<{
    feature: string;
    value: any;
    contribution: number;
    reason: string;
  }>;
  recommendation: string;
  processing_time_ms: number;
}

export interface DashboardStats {
  total_transactions: number;
  total_frauds: number;
  fraud_rate: number;
  total_amount: number;
  average_risk_score: number;
  recent_transactions: Transaction[];
  daily_trends: Array<{ date: string; fraud_count: number; total_count: number }>;
}

// Services spécifiques
export const fraudService = {
  // Détecter une fraude
  detectFraud: async (data: FraudDetectionRequest): Promise<FraudDetectionResponse> => {
    const response = await api.post('/detection/analyze', data);
    return response.data;
  },
  
  // Analyser en batch
  analyzeBatch: async (transactions: FraudDetectionRequest[]) => {
    const response = await api.post('/detection/batch', { transactions });
    return response.data;
  },
};

export const statsService = {
  // Récupérer les stats du dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/stats/dashboard');
    return response.data;
  },
  
  // Récupérer les tendances
  getTrends: async (days: number = 30) => {
    const response = await api.get(`/stats/trends?days=${days}`);
    return response.data;
  },
};

export const transactionService = {
  // Récupérer les transactions
  getTransactions: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    start_date?: string;
    end_date?: string;
    risk_level?: string;
  }) => {
    const response = await api.get('/transactions', { params });
    return response.data;
  },
  
  // Récupérer une transaction spécifique
  getTransaction: async (id: string) => {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },
  
  // Exporter les transactions
  exportToCSV: async (params?: any) => {
    const response = await api.get('/transactions/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

export const healthService = {
  // Vérifier la santé de l'API
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
  
  // Vérifier la connexion à la base de données
  checkDatabase: async () => {
    const response = await api.get('/health/db');
    return response.data;
  },
};

// Fonction utilitaire pour tester la connexion
export const testConnection = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.status === 200 && response.data.status === 'healthy';
  } catch (error) {
    console.error('Connection test failed:', error);
    return false;
  }
};

// Export par défaut
export default api;