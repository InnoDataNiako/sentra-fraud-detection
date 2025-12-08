/**
 * Composant de visualisation des fraudes - Version OPTIMISÉE
 * Utilise les données formatées du endpoint /stats/dashboard
 */

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, DollarSign, AlertTriangle, Activity, Users, Target } from 'lucide-react';

// ============================================================================
// TYPES POUR LES NOUVELLES DONNÉES
// ============================================================================

interface TrendData {
  date: string;
  total: number;
  fraud: number;
  fraudRate: number;
}

interface AmountDistribution {
  range: string;
  count: number;
  fraud_count: number;
}

interface RiskLevelData {
  name: string;
  value: number;
  color: string;
}

interface TransactionTypeData {
  type: string;
  total: number;
  fraud: number;
}

interface FraudChartProps {
  trendData?: TrendData[];
  amountDistribution?: AmountDistribution[];
  riskLevelData?: RiskLevelData[];
  transactionTypeData?: TransactionTypeData[];
  loading?: boolean;
}

// ============================================================================
// COMPOSANTS DE VISUALISATION
// ============================================================================

// Tooltip personnalisé pour les graphiques
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-900 mb-2">
          {label ? new Date(label).toLocaleDateString('fr-FR', { 
            weekday: 'short', 
            day: 'numeric', 
            month: 'short' 
          }) : label}
        </p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 mb-1">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm font-medium">{entry.name}:</span>
            <span className="text-sm">
              {typeof entry.value === 'number' 
                ? entry.value.toLocaleString('fr-FR') 
                : entry.value}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// Tooltip pour pie chart
const CustomPieTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-900">{payload[0].name}</p>
        <p className="text-sm">
          {payload[0].value.toLocaleString('fr-FR')} transactions
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {((payload[0].value / payload[0].payload.totalValue) * 100).toFixed(1)}% du total
        </p>
      </div>
    );
  }
  return null;
};

// ============================================================================
// COMPOSANT PRINCIPAL
// ============================================================================

export const FraudChart: React.FC<FraudChartProps> = ({
  trendData = [],
  amountDistribution = [],
  riskLevelData = [],
  transactionTypeData = [],
  loading = false
}) => {
  
  // Si chargement
  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map(i => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gray-100 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Si pas de données
  if (!trendData.length && !amountDistribution.length) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">Aucune donnée disponible</p>
              <p className="text-sm mt-2">
                Les graphiques s'afficheront une fois les données chargées
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Calculer le total des transactions pour les pourcentages
  const totalTransactions = riskLevelData.reduce((sum, item) => sum + item.value, 0);

  // ========== GRAPHIQUE 1 : ÉVOLUTION DES FRAUDES ==========
  const renderTrendChart = () => {
    if (!trendData.length) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Évolution des Transactions et Fraudes ({trendData.length} derniers jours)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                </linearGradient>
                <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('fr-FR', { 
                  month: 'short', 
                  day: 'numeric' 
                })}
                stroke="#64748b"
                fontSize={12}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                tickFormatter={(value) => value.toLocaleString('fr-FR')}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="total" 
                stroke="#3b82f6" 
                fill="url(#colorTotal)" 
                name="Total Transactions"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 6 }}
              />
              <Area 
                type="monotone" 
                dataKey="fraud" 
                stroke="#ef4444" 
                fill="url(#colorFraud)" 
                name="Fraudes Détectées"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 6 }}
              />
            </AreaChart>
          </ResponsiveContainer>
          
          {/* Statistiques rapides */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-700">
                {trendData.reduce((sum, day) => sum + day.total, 0).toLocaleString('fr-FR')}
              </div>
              <div className="text-sm text-blue-600">Transactions totales</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-700">
                {trendData.reduce((sum, day) => sum + day.fraud, 0).toLocaleString('fr-FR')}
              </div>
              <div className="text-sm text-red-600">Fraudes totales</div>
            </div>
            <div className="text-center p-3 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-700">
                {(trendData.reduce((sum, day) => sum + day.fraud, 0) / 
                  trendData.reduce((sum, day) => sum + day.total, 0) * 100).toFixed(2)}%
              </div>
              <div className="text-sm text-orange-600">Taux de fraude moyen</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-700">
                {Math.max(...trendData.map(d => d.fraud))}
              </div>
              <div className="text-sm text-green-600">Max fraudes/jour</div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  // ========== GRAPHIQUES 2 & 3 : DISTRIBUTION & NIVEAUX DE RISQUE ==========
  const renderDistributionCharts = () => {
    if (!amountDistribution.length || !riskLevelData.length) return null;

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution des Montants */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              Distribution des Montants (XOF)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={amountDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="range" 
                  stroke="#64748b"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#64748b"
                  fontSize={12}
                  tickFormatter={(value) => value.toLocaleString('fr-FR')}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar 
                  dataKey="count" 
                  fill="#3b82f6" 
                  name="Total Transactions" 
                  radius={[4, 4, 0, 0]}
                  barSize={40}
                />
                <Bar 
                  dataKey="fraud_count" 
                  fill="#ef4444" 
                  name="Transactions Frauduleuses" 
                  radius={[4, 4, 0, 0]}
                  barSize={40}
                />
              </BarChart>
            </ResponsiveContainer>
            
            {/* Légende détaillée */}
            <div className="mt-4 space-y-2">
              {amountDistribution.map((item, index) => {
                const fraudRate = item.count > 0 ? (item.fraud_count / item.count * 100) : 0;
                return (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <span className="font-medium">{item.range}</span>
                    <div className="flex items-center gap-4">
                      <span className="text-blue-600">{item.count.toLocaleString('fr-FR')}</span>
                      <span className="text-red-600">{item.fraud_count.toLocaleString('fr-FR')}</span>
                      <span className={`px-2 py-1 rounded text-xs ${fraudRate > 5 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                        {fraudRate.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Répartition par Niveau de Risque */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Répartition par Niveau de Risque
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col lg:flex-row items-center">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={riskLevelData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    innerRadius={40}
                    fill="#8884d8"
                    dataKey="value"
                    paddingAngle={2}
                  >
                    {riskLevelData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomPieTooltip />} />
                </PieChart>
              </ResponsiveContainer>

              {/* Légende avec statistiques */}
              <div className="lg:ml-6 mt-4 lg:mt-0 space-y-3 w-full">
                {riskLevelData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-2 rounded hover:bg-gray-50">
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-4 h-4 rounded" 
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="font-medium text-gray-700">{item.name}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{item.value.toLocaleString('fr-FR')}</div>
                      <div className="text-xs text-gray-500">
                        {((item.value / totalTransactions) * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ))}
                <div className="pt-3 border-t">
                  <div className="flex justify-between font-semibold">
                    <span>Total</span>
                    <span>{totalTransactions.toLocaleString('fr-FR')} transactions</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  // ========== GRAPHIQUE 4 : FRAUDES PAR TYPE DE TRANSACTION ==========
  const renderTransactionTypeChart = () => {
    if (!transactionTypeData.length) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-600" />
            Fraudes par Type de Transaction
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart 
              data={transactionTypeData}
              layout="vertical"
              margin={{ left: 80, right: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis 
                type="number" 
                stroke="#64748b"
                fontSize={12}
                tickFormatter={(value) => value.toLocaleString('fr-FR')}
              />
              <YAxis 
                dataKey="type" 
                type="category" 
                stroke="#64748b"
                fontSize={12}
                width={80}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar 
                dataKey="total" 
                fill="#3b82f6" 
                name="Total Transactions" 
                radius={[0, 4, 4, 0]}
                barSize={25}
              />
              <Bar 
                dataKey="fraud" 
                fill="#ef4444" 
                name="Transactions Frauduleuses" 
                radius={[0, 4, 4, 0]}
                barSize={25}
              />
            </BarChart>
          </ResponsiveContainer>
          
          {/* Tableau des taux de fraude */}
          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="p-2 text-left">Type</th>
                  <th className="p-2 text-right">Total</th>
                  <th className="p-2 text-right">Fraudes</th>
                  <th className="p-2 text-right">Taux</th>
                  <th className="p-2 text-right">Risque</th>
                </tr>
              </thead>
              <tbody>
                {transactionTypeData.map((item, index) => {
                  const fraudRate = item.total > 0 ? (item.fraud / item.total * 100) : 0;
                  let riskLevel = "Faible";
                  let riskColor = "bg-green-100 text-green-800";
                  
                  if (fraudRate > 10) {
                    riskLevel = "Critique";
                    riskColor = "bg-red-100 text-red-800";
                  } else if (fraudRate > 5) {
                    riskLevel = "Élevé";
                    riskColor = "bg-orange-100 text-orange-800";
                  } else if (fraudRate > 2) {
                    riskLevel = "Moyen";
                    riskColor = "bg-yellow-100 text-yellow-800";
                  }
                  
                  return (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="p-2 font-medium">{item.type}</td>
                      <td className="p-2 text-right">{item.total.toLocaleString('fr-FR')}</td>
                      <td className="p-2 text-right text-red-600">{item.fraud.toLocaleString('fr-FR')}</td>
                      <td className="p-2 text-right font-semibold">{fraudRate.toFixed(2)}%</td>
                      <td className="p-2 text-right">
                        <span className={`px-2 py-1 rounded text-xs ${riskColor}`}>
                          {riskLevel}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    );
  };

  // ========== GRAPHIQUE 5 : TAUX DE FRAUDE ==========
  const renderFraudRateChart = () => {
    if (!trendData.length) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-red-600" />
            Évolution du Taux de Fraude (%) 
            <span className="text-sm font-normal text-gray-500 ml-2">
              Moyenne: {(trendData.reduce((sum, day) => sum + day.fraudRate, 0) / trendData.length).toFixed(2)}%
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('fr-FR', { 
                  month: 'short', 
                  day: 'numeric' 
                })}
                stroke="#64748b"
                fontSize={12}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                tickFormatter={(value) => `${value}%`}
                domain={[0, 'dataMax + 1']}
              />
              <Tooltip 
                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Taux de fraude']}
                labelFormatter={(label) => new Date(label).toLocaleDateString('fr-FR', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long'
                })}
              />
              <Line 
                type="monotone" 
                dataKey="fraudRate" 
                stroke="#ef4444" 
                strokeWidth={3}
                name="Taux de Fraude"
                dot={{ fill: '#ef4444', r: 4, strokeWidth: 2 }}
                activeDot={{ r: 8, fill: '#dc2626' }}
              />
              {/* Ligne de moyenne */}
              <Line 
                type="monotone"
                dataKey={() => trendData.reduce((sum, day) => sum + day.fraudRate, 0) / trendData.length}
                stroke="#94a3b8"
                strokeWidth={1}
                strokeDasharray="5 5"
                name="Moyenne"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
          
          {/* Statistiques du taux */}
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="text-center p-2 bg-red-50 rounded">
              <div className="text-lg font-bold text-red-700">
                {Math.max(...trendData.map(d => d.fraudRate)).toFixed(2)}%
              </div>
              <div className="text-xs text-red-600">Taux max</div>
            </div>
            <div className="text-center p-2 bg-green-50 rounded">
              <div className="text-lg font-bold text-green-700">
                {Math.min(...trendData.map(d => d.fraudRate)).toFixed(2)}%
              </div>
              <div className="text-xs text-green-600">Taux min</div>
            </div>
            <div className="text-center p-2 bg-blue-50 rounded">
              <div className="text-lg font-bold text-blue-700">
                {(trendData.reduce((sum, day) => sum + day.fraudRate, 0) / trendData.length).toFixed(2)}%
              </div>
              <div className="text-xs text-blue-600">Moyenne</div>
            </div>
            <div className="text-center p-2 bg-purple-50 rounded">
              <div className="text-lg font-bold text-purple-700">
                {trendData.filter(d => d.fraudRate > 5).length}
              </div>
              <div className="text-xs text-purple-600">Jours &gt; 5%</div>

            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  // ============================================================================
  // RENDU PRINCIPAL
  // ============================================================================

  return (
    <div className="space-y-6">
      {renderTrendChart()}
      {renderDistributionCharts()}
      {renderTransactionTypeChart()}
      {renderFraudRateChart()}
    </div>
  );
};