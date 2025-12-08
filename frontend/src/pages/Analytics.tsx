/**
 * Page Analytics SÉNTRA - Version FINALE OPTIMISÉE
 * Utilise le nouvel endpoint /stats/dashboard pour toutes les données
 * Affiche TOUTES les transactions de la base de données
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  RefreshCw, TrendingUp, AlertCircle, Calendar, Database, ShieldAlert,
  Percent, TrendingDown, Download, CheckCircle, X, Bell, BellOff,
  FileSpreadsheet, Eye, ArrowUpDown, Filter, ChevronDown
} from 'lucide-react';

import { FraudChart } from '@/components/FraudChart';
import { RecentTransactions } from '@/components/RecentTransactions';
import { fraudService } from '@/services/fraudService';
import { Transaction } from '@/types/fraud';
import { TransactionDetails } from '@/components/TransactionDetails';

// ============================================================================
// TYPES
// ============================================================================

interface DashboardData {
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

// ============================================================================
// COMPOSANT PRINCIPAL
// ============================================================================

export const Analytics: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);


  // ========== CHARGEMENT DES DONNÉES ==========
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('📊 Chargement du dashboard...');
      
      // 🔥 UN SEUL APPEL pour TOUT le dashboard
      const dashboardResponse = await fetch('/api/v1/stats/dashboard');
      
      if (!dashboardResponse.ok) {
        const errorData = await dashboardResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erreur API: ${dashboardResponse.status}`);
      }
      
      const data: DashboardData = await dashboardResponse.json();
      setDashboardData(data);
      setLastUpdate(new Date());
      
      console.log('✅ Dashboard data loaded:', data);
      console.log(`📈 Total transactions en base: ${data.total_transactions_in_db}`);
      
      // Charger les transactions récentes (max 100 pour le tableau)
      try {
        const transactionsResponse = await fraudService.getTransactions(
          {},
          { page: 1, page_size: 100 }
        );
        setRecentTransactions(transactionsResponse.items || []);
        console.log(`📋 ${transactionsResponse.items?.length || 0} transactions récentes chargées`);
      } catch (txError) {
        console.warn('⚠️ Could not load recent transactions:', txError);
        // C'est ok, on a déjà les données principales
      }
      
    } catch (err: any) {
      console.error('❌ Error loading dashboard:', err);
      setError(err.message || 'Impossible de charger les données analytics');
    } finally {
      setLoading(false);
    }
  };

  // Charger au montage
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Auto-refresh toutes les 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('🔄 Auto-refresh dashboard...');
      loadDashboardData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  // ========== FORMATAGE ==========
  const formatAmount = (amount: number) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M XOF`;
    }
    return `${amount.toLocaleString('fr-FR')} XOF`;
  };

  const formatNumber = (num: number) => {
    return num.toLocaleString('fr-FR');
  };

  // ========== CARTES DE STATISTIQUES ==========
  const getStatsCards = () => {
    if (!dashboardData) return null;
    
    const { summary } = dashboardData.summary;
    
    return [
      {
        title: "Total Transactions",
        value: formatNumber(summary.total_transactions),
        icon: Database,
        color: "text-blue-600",
        bgColor: "bg-blue-50",
        description: "Base de données complète",
        trend: null
      },
      {
        title: "Fraudes Détectées",
        value: formatNumber(summary.fraud_transactions),
        icon: ShieldAlert,
        color: "text-red-600",
        bgColor: "bg-red-50",
        description: `${summary.fraud_rate.toFixed(2)}% du total`,
        trend: "danger"
      },
      {
        title: "Taux de Fraude",
        value: `${summary.fraud_rate.toFixed(2)}%`,
        icon: Percent,
        color: "text-orange-600",
        bgColor: "bg-orange-50",
        description: `Score moyen: ${summary.avg_fraud_score.toFixed(1)}%`,
        trend: summary.fraud_rate > 5 ? "danger" : "success"
      },
      {
        title: "Montant Total",
        value: formatAmount(summary.total_amount),
        icon: TrendingUp,
        color: "text-green-600",
        bgColor: "bg-green-50",
        description: `Moy: ${formatAmount(summary.avg_amount)}`,
        trend: "success"
      },
      {
        title: "Dernières 24h",
        value: formatNumber(summary.last_24h.transactions),
        icon: Calendar,
        color: "text-purple-600",
        bgColor: "bg-purple-50",
        description: `${summary.last_24h.frauds} fraudes (${summary.last_24h.fraud_rate.toFixed(1)}%)`,
        trend: null
      },
      {
        title: "Score Moyen",
        value: `${summary.avg_fraud_score.toFixed(1)}%`,
        icon: TrendingDown,
        color: "text-indigo-600",
        bgColor: "bg-indigo-50",
        description: "Risque de fraude moyen",
        trend: summary.avg_fraud_score > 50 ? "danger" : "success"
      }
    ];
  };

  // ========== DONNÉES POUR LES GRAPHIQUES ==========
  const getChartData = () => {
    if (!dashboardData) return null;
    
    const { trends, by_type, score_distribution, summary } = dashboardData;
    
    return {
      trendData: trends.daily_data.map(day => ({
        date: day.date,
        total: day.total,
        fraud: day.fraud,
        fraudRate: day.fraud_rate
      })),
      
      amountDistribution: summary.amount_distribution,
      
      riskLevelData: score_distribution.distribution.map(item => ({
        name: item.level,
        value: item.count,
        color: item.color
      })),
      
      transactionTypeData: by_type.by_type.map(type => ({
        type: type.type,
        total: type.total,
        fraud: type.fraud
      }))
    };
  };

  // ========== EXPORT DES DONNÉES ==========
  const exportData = () => {
    if (!dashboardData) return;
    
    const exportData = {
      exported_at: new Date().toISOString(),
      summary: dashboardData.summary,
      trends: dashboardData.trends,
      by_type: dashboardData.by_type,
      score_distribution: dashboardData.score_distribution,
      top_stats: dashboardData.top_stats
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
  };

  // ========== RENDU - ÉTAT DE CHARGEMENT ==========
  if (loading && !dashboardData) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <RefreshCw className="h-12 w-12 animate-spin text-blue-600 mb-4" />
        <p className="text-lg text-gray-600 font-semibold">Chargement des analytics...</p>
        <p className="text-sm text-gray-500 mt-2">
          Analyse de toutes les transactions de la base de données
        </p>
        <div className="mt-4 flex gap-2">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    );
  }

  // ========== RENDU - ÉTAT D'ERREUR ==========
  if (error) {
    return (
      <div className="m-6">
        <Alert className="border-red-300 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <div className="font-semibold mb-2">❌ Erreur de chargement</div>
            <div className="mb-3">{error}</div>
            <div className="space-y-2">
              <p className="text-sm">Vérifiez que :</p>
              <ul className="text-sm list-disc list-inside space-y-1 ml-2">
                <li>Le backend est démarré (port 8000)</li>
                <li>L'endpoint <code className="bg-red-100 px-1 py-0.5 rounded">/api/v1/stats/dashboard</code> est accessible</li>
                <li>La base de données contient des transactions</li>
              </ul>
            </div>
            <Button 
              onClick={loadDashboardData} 
              variant="outline" 
              size="sm" 
              className="mt-4 gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Réessayer
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // ========== RENDU - DONNÉES VIDES ==========
  if (!dashboardData) {
    return (
      <div className="m-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Aucune donnée à afficher. Vérifiez la connexion au backend.
          </AlertDescription>
        </Alert>
      </div>
    );
  }
  
  const statsCards = getStatsCards();
  const chartData = getChartData();

  // ========== RENDU PRINCIPAL ==========
  return (
    <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
      {/* ========== EN-TÊTE ========== */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              📊 Analytics & Visualisations
            </h1>
            <div className="flex flex-wrap items-center gap-3">
              <p className="text-gray-600">
                Analyse complète de <span className="font-bold text-blue-600">
                  {formatNumber(dashboardData.summary.summary.total_transactions)}
                </span> transactions
              </p>
              <span className="text-xs bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-medium">
                {formatNumber(dashboardData.total_transactions_in_db)} en base de données
              </span>
              {lastUpdate && (
                <span className="text-xs bg-green-100 text-green-800 px-3 py-1 rounded-full font-medium flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  Mis à jour: {lastUpdate.toLocaleTimeString('fr-FR')}
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={loadDashboardData}
              disabled={loading}
              variant="outline"
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Actualiser
            </Button>
            <Button 
              onClick={exportData}
              className="gap-2 bg-blue-600 hover:bg-blue-700"
            >
              <Download className="h-4 w-4" />
              Exporter JSON
            </Button>
          </div>
        </div>
      </div>

      {/* ========== CARTES DE STATISTIQUES ========== */}
      {statsCards && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {statsCards.map((stat, index) => (
            <Card 
              key={index} 
              className="overflow-hidden hover:shadow-lg transition-all duration-200 border-l-4"
              style={{ borderLeftColor: stat.color.replace('text-', '#') }}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-xs text-gray-600 font-medium uppercase tracking-wide mb-1">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 mb-1">
                      {stat.value}
                    </p>
                    <p className="text-xs text-gray-500">
                      {stat.description}
                    </p>
                  </div>
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <stat.icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* ========== GRAPHIQUES PRINCIPAUX ========== */}
      {chartData && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">
                Vue d'ensemble des fraudes
              </h2>
              <p className="text-sm text-gray-500">
                Visualisations détaillées sur {dashboardData.trends.period_days} jours
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Données générées le</p>
              <p className="text-sm font-medium text-gray-700">
                {new Date(dashboardData.generated_at).toLocaleString('fr-FR')}
              </p>
            </div>
          </div>
          
          <FraudChart
            trendData={chartData.trendData}
            amountDistribution={chartData.amountDistribution}
            riskLevelData={chartData.riskLevelData}
            transactionTypeData={chartData.transactionTypeData}
            loading={loading}
          />
        </div>
      )}

      {/* ========== TOP STATISTIQUES ========== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Clients Frauduleux */}
        <Card className="shadow-sm">
          <CardContent className="p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-red-600" />
              Top 10 Clients Frauduleux
            </h3>
            <div className="space-y-2">
              {dashboardData.top_stats.top_fraudulent_clients.slice(0, 10).map((client, index) => (
                <div 
                  key={client.customer_id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                >
                  <div className="flex items-center gap-3">
                    <div className={`
                      w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                      ${index < 3 ? 'bg-red-100 text-red-700' : 'bg-gray-200 text-gray-600'}
                    `}>
                      {index + 1}
                    </div>
                    <div>
                      <div className="font-medium text-sm">{client.customer_id}</div>
                      <div className="text-xs text-gray-500">
                        {client.total_transactions} transactions
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-red-600 text-sm">
                      {client.fraud_count} fraudes
                    </div>
                    <div className="text-xs text-red-500">
                      {client.fraud_rate.toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Transactions Frauduleuses */}
        <Card className="shadow-sm">
          <CardContent className="p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-orange-600" />
              Top 10 Fraudes (Montant)
            </h3>
            <div className="space-y-2">
              {dashboardData.top_stats.top_fraud_transactions.slice(0, 10).map((tx, index) => (
                <div 
                  key={tx.transaction_id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                >
                  <div className="flex items-center gap-3">
                    <div className={`
                      w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                      ${index < 3 ? 'bg-orange-100 text-orange-700' : 'bg-gray-200 text-gray-600'}
                    `}>
                      {index + 1}
                    </div>
                    <div>
                      <div className="font-medium text-sm">{tx.transaction_id}</div>
                      <div className="text-xs text-gray-500">{tx.customer_id}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-orange-600 text-sm">
                      {formatAmount(tx.amount)}
                    </div>
                    <div className="text-xs text-orange-500">
                      Score: {tx.fraud_score.toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ========== TABLEAU DES TRANSACTIONS RÉCENTES ========== */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">
            Transactions Récentes
          </h2>
          <p className="text-sm text-gray-500">
            Dernières {recentTransactions.length} transactions de la base de données
          </p>
        </div>
        {/* <RecentTransactions 
          transactions={recentTransactions}
          onViewDetails={(transaction) => {
            console.log('Voir détails transaction:', transaction);
            // TODO: Ouvrir modale avec détails
          }}
        /> */}
          <RecentTransactions 
          transactions={recentTransactions}
          onViewDetails={(transaction) => {
            setSelectedTransaction(transaction);
          }}
        />
      </div>

      {/* ========== FOOTER ========== */}
      <div className="text-center text-sm text-gray-500 py-6 border-t bg-white rounded-lg">
        <p className="mb-2">
          <strong>SÉNTRA</strong> - Système de Détection de Fraude
        </p>
        <p>
          Données générées le {new Date(dashboardData.generated_at).toLocaleString('fr-FR')} • 
          Base de données: {formatNumber(dashboardData.total_transactions_in_db)} transactions
        </p>
      </div>
       {/* ========== MODALE DE DÉTAILS ========== */}
      {selectedTransaction && (
        <TransactionDetails
          transaction={selectedTransaction}
          isOpen={!!selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
        />
      )}
    </div>
  );
};


// ============================================================================
// COMPOSANT MODAL DÉTAILS TRANSACTION
// ============================================================================
const TransactionDetailsModal = ({ transaction, onClose }) => {
  if (!transaction) return null;

  const getFraudColor = (score) => {
    if (score >= 80) return 'text-red-600 bg-red-50';
    if (score >= 60) return 'text-orange-600 bg-orange-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Détails de la Transaction</h2>
            <p className="text-sm text-gray-500">{transaction.transaction_id}</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Statut Fraude */}
          <div className={`p-4 rounded-lg border-2 ${
            transaction.is_fraud 
              ? 'bg-red-50 border-red-300' 
              : 'bg-green-50 border-green-300'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <ShieldAlert className={`h-8 w-8 ${
                  transaction.is_fraud ? 'text-red-600' : 'text-green-600'
                }`} />
                <div>
                  <h3 className="text-lg font-bold">
                    {transaction.is_fraud ? '🚨 TRANSACTION FRAUDULEUSE' : '✅ Transaction Légitime'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Score de fraude: {transaction.fraud_score}%
                  </p>
                </div>
              </div>
              <div className={`px-4 py-2 rounded-full font-bold text-lg ${getFraudColor(transaction.fraud_score)}`}>
                {transaction.fraud_score}%
              </div>
            </div>
          </div>

          {/* Informations Transaction */}
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardContent className="p-4">
                <p className="text-xs text-gray-500 mb-1">Montant</p>
                <p className="text-2xl font-bold text-gray-900">
                  {transaction.amount?.toLocaleString('fr-FR')} XOF
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <p className="text-xs text-gray-500 mb-1">Type</p>
                <p className="text-lg font-semibold text-gray-900 capitalize">
                  {transaction.transaction_type?.replace('_', ' ')}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Informations Client */}
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-3">👤 Informations Client</h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">ID Client:</span>
                <span className="font-semibold">{transaction.customer_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Localisation:</span>
                <span className="font-semibold">{transaction.location || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Appareil:</span>
                <span className="font-semibold">{transaction.device_id || 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* Détails Temporels */}
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-3">🕐 Informations Temporelles</h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Date:</span>
                <span className="font-semibold">
                  {new Date(transaction.created_at).toLocaleDateString('fr-FR', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                  })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Heure:</span>
                <span className="font-semibold">
                  {new Date(transaction.created_at).toLocaleTimeString('fr-FR')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Heure de la journée:</span>
                <span className="font-semibold">{transaction.time_of_day || 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* Caractéristiques de Risque */}
          {transaction.is_fraud && (
            <div>
              <h3 className="text-lg font-bold text-red-600 mb-3">⚠️ Indicateurs de Risque</h3>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 space-y-2">
                {transaction.amount > 500000 && (
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-red-600 rounded-full"></div>
                    <span className="text-sm">Montant exceptionnellement élevé (&gt;500k XOF)</span>
                  </div>
                )}
                {transaction.fraud_score > 80 && (
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-red-600 rounded-full"></div>
                    <span className="text-sm">Score de fraude très élevé (&gt;80%)</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-600 rounded-full"></div>
                  <span className="text-sm">Marquée comme frauduleuse par le modèle ML</span>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button 
              onClick={onClose}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              Fermer
            </Button>
            <Button 
              variant="outline"
              className="flex-1"
              onClick={() => {
                navigator.clipboard.writeText(transaction.transaction_id);
                alert('ID copié !');
              }}
            >
              Copier l'ID
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// COMPOSANT ALERTES TEMPS RÉEL
// ============================================================================
const FraudAlerts = ({ transactions, enabled, onToggle }) => {
  const [alerts, setAlerts] = useState([]);
  const [dismissed, setDismissed] = useState(new Set());

  useEffect(() => {
    if (!enabled || !transactions?.length) return;

    // Filtrer les fraudes critiques (score > 80%)
    const criticalFrauds = transactions
      .filter(t => t.is_fraud && t.fraud_score > 80)
      .slice(0, 5);

    setAlerts(criticalFrauds);
  }, [transactions, enabled]);

  const visibleAlerts = alerts.filter(a => !dismissed.has(a.transaction_id));

  if (!enabled) return null;

  return (
    <div className="fixed top-20 right-6 w-96 space-y-2 z-40">
      {visibleAlerts.map(alert => (
        <Alert key={alert.transaction_id} className="bg-red-50 border-red-300 shadow-lg animate-in slide-in-from-right">
          <div className="flex items-start gap-3">
            <ShieldAlert className="h-5 w-5 text-red-600 mt-1" />
            <div className="flex-1">
              <div className="font-bold text-red-900">🚨 Fraude Critique Détectée</div>
              <div className="text-sm text-red-800 mt-1">
                <div>Transaction: {alert.transaction_id}</div>
                <div>Montant: {alert.amount?.toLocaleString()} XOF</div>
                <div>Score: {alert.fraud_score}%</div>
              </div>
            </div>
            <button
              onClick={() => setDismissed(prev => new Set(prev).add(alert.transaction_id))}
              className="p-1 hover:bg-red-100 rounded"
            >
              <X className="h-4 w-4 text-red-600" />
            </button>
          </div>
        </Alert>
      ))}
    </div>
  );
};

// ============================================================================
// COMPOSANT COMPARAISON TEMPORELLE
// ============================================================================
const TemporalComparison = ({ dailyData }) => {
  if (!dailyData?.length) return null;

  // Calculer cette semaine vs semaine dernière
  const today = new Date();
  const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
  const fourteenDaysAgo = new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000);

  const thisWeek = dailyData.filter(d => new Date(d.date) >= sevenDaysAgo);
  const lastWeek = dailyData.filter(d => {
    const date = new Date(d.date);
    return date >= fourteenDaysAgo && date < sevenDaysAgo;
  });

  const thisWeekStats = {
    total: thisWeek.reduce((sum, d) => sum + d.total, 0),
    fraud: thisWeek.reduce((sum, d) => sum + d.fraud, 0),
    amount: thisWeek.reduce((sum, d) => sum + d.total_amount, 0)
  };

  const lastWeekStats = {
    total: lastWeek.reduce((sum, d) => sum + d.total, 0),
    fraud: lastWeek.reduce((sum, d) => sum + d.fraud, 0),
    amount: lastWeek.reduce((sum, d) => sum + d.total_amount, 0)
  };

  const calcChange = (current, previous) => {
    if (previous === 0) return 0;
    return ((current - previous) / previous * 100).toFixed(1);
  };

  const totalChange = calcChange(thisWeekStats.total, lastWeekStats.total);
  const fraudChange = calcChange(thisWeekStats.fraud, lastWeekStats.fraud);
  const amountChange = calcChange(thisWeekStats.amount, lastWeekStats.amount);

  return (
    <Card className="shadow-sm">
      <CardContent className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-purple-600" />
          Comparaison Hebdomadaire
        </h3>
        
        <div className="grid grid-cols-3 gap-4">
          {/* Transactions */}
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-xs text-blue-600 font-medium mb-1">Transactions</p>
            <p className="text-2xl font-bold text-blue-900 mb-1">{thisWeekStats.total}</p>
            <div className={`text-sm font-medium ${parseFloat(totalChange) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {parseFloat(totalChange) >= 0 ? '↗' : '↘'} {Math.abs(totalChange)}%
            </div>
            <p className="text-xs text-gray-600 mt-1">vs semaine dernière: {lastWeekStats.total}</p>
          </div>

          {/* Fraudes */}
          <div className="bg-red-50 rounded-lg p-4">
            <p className="text-xs text-red-600 font-medium mb-1">Fraudes</p>
            <p className="text-2xl font-bold text-red-900 mb-1">{thisWeekStats.fraud}</p>
            <div className={`text-sm font-medium ${parseFloat(fraudChange) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
              {parseFloat(fraudChange) >= 0 ? '↗' : '↘'} {Math.abs(fraudChange)}%
            </div>
            <p className="text-xs text-gray-600 mt-1">vs semaine dernière: {lastWeekStats.fraud}</p>
          </div>

          {/* Montant */}
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-xs text-green-600 font-medium mb-1">Montant</p>
            <p className="text-xl font-bold text-green-900 mb-1">
              {(thisWeekStats.amount / 1000000).toFixed(1)}M
            </p>
            <div className={`text-sm font-medium ${parseFloat(amountChange) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {parseFloat(amountChange) >= 0 ? '↗' : '↘'} {Math.abs(amountChange)}%
            </div>
            <p className="text-xs text-gray-600 mt-1">vs semaine dernière: {(lastWeekStats.amount / 1000000).toFixed(1)}M</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};