import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, PieChart, Pie, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import { 
  Brain, TrendingUp, TrendingDown, AlertCircle, 
  Info, Lightbulb, Shield, DollarSign, Clock,
  MapPin, Smartphone, User, Activity
} from 'lucide-react';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

interface ShapValue {
  feature: string;
  value: number;
  actual_value: any;
  contribution: number;
  importance: 'critical' | 'high' | 'medium' | 'low';
  icon?: any;
  description: string;
}

interface ExplanationData {
  transaction_id: string;
  prediction: number;
  base_value: number;
  shap_values: ShapValue[];
  risk_factors: string[];
  protective_factors: string[];
  confidence: number;
  verdict: 'fraud' | 'legitimate' | 'suspicious';
}

// ============================================================================
// COMPOSANT 1: SHAP BAR CHART (Force Plot Style)
// ============================================================================

const ShapForceChart: React.FC<{ shapValues: ShapValue[] }> = ({ shapValues }) => {
  const sortedValues = [...shapValues].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));
  
  const data = sortedValues.map(sv => ({
    name: sv.feature,
    contribution: sv.contribution,
    absContribution: Math.abs(sv.contribution),
    fill: sv.contribution > 0 ? '#EF4444' : '#10B981'
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.[0]) return null;
    
    const data = payload[0].payload;
    const shapValue = sortedValues.find(sv => sv.feature === data.name);
    
    return (
      <div className="bg-white p-4 rounded-lg shadow-lg border-2 border-gray-200">
        <p className="font-bold text-gray-900 mb-2">{data.name}</p>
        <div className="space-y-1 text-sm">
          <p className="text-gray-600">
            Valeur: <strong>{shapValue?.actual_value}</strong>
          </p>
          <p className={data.contribution > 0 ? 'text-red-600' : 'text-green-600'}>
            Contribution: <strong>{data.contribution > 0 ? '+' : ''}{data.contribution.toFixed(3)}</strong>
          </p>
          <p className="text-gray-500 text-xs mt-2">
            {shapValue?.description}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full h-80">
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 100, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={90} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// ============================================================================
// COMPOSANT 2: FEATURE IMPORTANCE PIE CHART
// ============================================================================

const FeatureImportancePie: React.FC<{ shapValues: ShapValue[] }> = ({ shapValues }) => {
  const data = shapValues
    .map(sv => ({
      name: sv.feature,
      value: Math.abs(sv.contribution),
      color: getImportanceColor(sv.importance)
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6); // Top 6 features

  const COLORS = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
};

// ============================================================================
// COMPOSANT 3: RADAR CHART (Vue d'ensemble)
// ============================================================================

const RiskRadarChart: React.FC<{ shapValues: ShapValue[] }> = ({ shapValues }) => {
  const topFeatures = shapValues
    .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
    .slice(0, 6);

  const data = topFeatures.map(sv => ({
    feature: sv.feature,
    risk: Math.abs(sv.contribution) * 100,
    fullMark: 10
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="feature" />
        <PolarRadiusAxis angle={90} domain={[0, 10]} />
        <Radar name="Niveau de Risque" dataKey="risk" stroke="#EF4444" fill="#EF4444" fillOpacity={0.6} />
        <Tooltip />
      </RadarChart>
    </ResponsiveContainer>
  );
};

// ============================================================================
// COMPOSANT 4: FEATURE CARDS (Détails des contributions)
// ============================================================================

const FeatureCard: React.FC<{ shapValue: ShapValue }> = ({ shapValue }) => {
  const isRisk = shapValue.contribution > 0;
  const Icon = shapValue.icon || Activity;
  
  return (
    <Card className={`border-l-4 ${isRisk ? 'border-l-red-500 bg-red-50' : 'border-l-green-500 bg-green-50'}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-lg ${isRisk ? 'bg-red-100' : 'bg-green-100'}`}>
              <Icon className={`h-4 w-4 ${isRisk ? 'text-red-600' : 'text-green-600'}`} />
            </div>
            <div>
              <p className="font-semibold text-sm text-gray-900">{shapValue.feature}</p>
              <p className="text-xs text-gray-600">{shapValue.actual_value}</p>
            </div>
          </div>
          <Badge variant={isRisk ? 'destructive' : 'secondary'} className="text-xs">
            {shapValue.importance.toUpperCase()}
          </Badge>
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Impact:</span>
            <span className={`font-bold ${isRisk ? 'text-red-600' : 'text-green-600'}`}>
              {isRisk ? '+' : ''}{(shapValue.contribution * 100).toFixed(1)}%
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${isRisk ? 'bg-red-500' : 'bg-green-500'}`}
              style={{ width: `${Math.min(Math.abs(shapValue.contribution) * 100, 100)}%` }}
            />
          </div>
          
          <p className="text-xs text-gray-600 mt-2">{shapValue.description}</p>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// COMPOSANT PRINCIPAL: EXPLAINABILITY PANEL
// ============================================================================

const ExplainabilityPanel: React.FC<{ transaction: any }> = ({ transaction }) => {
  const [explanationData, setExplanationData] = useState<ExplanationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'charts'>('overview');

  useEffect(() => {
    // Simuler l'appel API pour récupérer les valeurs SHAP
    // Dans la vraie app, remplacer par: await api.get(`/explain/${transaction.id}`)
    const mockExplanation = generateMockShapValues(transaction);
    setExplanationData(mockExplanation);
    setLoading(false);
  }, [transaction]);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <Brain className="h-12 w-12 animate-pulse text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Analyse des contributions SHAP en cours...</p>
        </CardContent>
      </Card>
    );
  }

  if (!explanationData) return null;

  const riskFactors = explanationData.shap_values.filter(sv => sv.contribution > 0);
  const protectiveFactors = explanationData.shap_values.filter(sv => sv.contribution < 0);

  return (
    <div className="space-y-6">
      {/* En-tête avec verdict */}
      <Card className={`border-2 ${
        explanationData.verdict === 'fraud' ? 'border-red-500 bg-red-50' :
        explanationData.verdict === 'suspicious' ? 'border-orange-500 bg-orange-50' :
        'border-green-500 bg-green-50'
      }`}>
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-full ${
                explanationData.verdict === 'fraud' ? 'bg-red-100' :
                explanationData.verdict === 'suspicious' ? 'bg-orange-100' :
                'bg-green-100'
              }`}>
                <Brain className={`h-8 w-8 ${
                  explanationData.verdict === 'fraud' ? 'text-red-600' :
                  explanationData.verdict === 'suspicious' ? 'text-orange-600' :
                  'text-green-600'
                }`} />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-1">
                  {explanationData.verdict === 'fraud' ? '🚨 Transaction Frauduleuse' :
                   explanationData.verdict === 'suspicious' ? '⚠️ Transaction Suspecte' :
                   '✅ Transaction Légitime'}
                </h3>
                <p className="text-sm text-gray-600">
                  Probabilité de fraude: <strong>{(explanationData.prediction * 100).toFixed(1)}%</strong>
                  {' • '}
                  Confiance du modèle: <strong>{(explanationData.confidence * 100).toFixed(0)}%</strong>
                </p>
              </div>
            </div>
            <Badge className="text-lg px-4 py-2">
              Score: {(explanationData.prediction * 100).toFixed(1)}%
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Navigation par onglets */}
      <div className="flex gap-2 border-b">
        <Button
          variant={activeTab === 'overview' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('overview')}
          className="gap-2"
        >
          <Lightbulb className="h-4 w-4" />
          Vue d'ensemble
        </Button>
        <Button
          variant={activeTab === 'details' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('details')}
          className="gap-2"
        >
          <Info className="h-4 w-4" />
          Détails
        </Button>
        <Button
          variant={activeTab === 'charts' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('charts')}
          className="gap-2"
        >
          <Activity className="h-4 w-4" />
          Visualisations
        </Button>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Facteurs de Risque */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <AlertCircle className="h-5 w-5" />
                Facteurs de Risque ({riskFactors.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {riskFactors.slice(0, 5).map((factor, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-red-600" />
                      <div>
                        <p className="font-medium text-sm">{factor.feature}</p>
                        <p className="text-xs text-gray-600">{factor.actual_value}</p>
                      </div>
                    </div>
                    <Badge variant="destructive">
                      +{(factor.contribution * 100).toFixed(1)}%
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Facteurs Protecteurs */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <Shield className="h-5 w-5" />
                Facteurs Protecteurs ({protectiveFactors.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {protectiveFactors.slice(0, 5).map((factor, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <TrendingDown className="h-4 w-4 text-green-600" />
                      <div>
                        <p className="font-medium text-sm">{factor.feature}</p>
                        <p className="text-xs text-gray-600">{factor.actual_value}</p>
                      </div>
                    </div>
                    <Badge className="bg-green-100 text-green-800">
                      {(factor.contribution * 100).toFixed(1)}%
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'details' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {explanationData.shap_values.map((sv, idx) => (
            <FeatureCard key={idx} shapValue={sv} />
          ))}
        </div>
      )}

      {activeTab === 'charts' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Contribution des Features (Force Plot)</CardTitle>
            </CardHeader>
            <CardContent>
              <ShapForceChart shapValues={explanationData.shap_values} />
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Importance Relative</CardTitle>
              </CardHeader>
              <CardContent>
                <FeatureImportancePie shapValues={explanationData.shap_values} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Vue Radar des Risques</CardTitle>
              </CardHeader>
              <CardContent>
                <RiskRadarChart shapValues={explanationData.shap_values} />
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Explications en langage naturel */}
      <Alert>
        <Lightbulb className="h-4 w-4" />
        <AlertDescription>
          <p className="font-semibold mb-2">💡 Explication en langage clair:</p>
          <p className="text-sm text-gray-700">
            {generateNaturalExplanation(explanationData)}
          </p>
        </AlertDescription>
      </Alert>
    </div>
  );
};

// ============================================================================
// FONCTIONS UTILITAIRES
// ============================================================================

const getImportanceColor = (importance: string) => {
  switch (importance) {
    case 'critical': return '#EF4444';
    case 'high': return '#F59E0B';
    case 'medium': return '#10B981';
    case 'low': return '#3B82F6';
    default: return '#6B7280';
  }
};

const generateNaturalExplanation = (data: ExplanationData) => {
  const topRisk = data.shap_values
    .filter(sv => sv.contribution > 0)
    .sort((a, b) => b.contribution - a.contribution)[0];
  
  const topProtective = data.shap_values
    .filter(sv => sv.contribution < 0)
    .sort((a, b) => a.contribution - b.contribution)[0];

  if (data.verdict === 'fraud') {
    return `Cette transaction a été classée comme frauduleuse principalement à cause de ${topRisk?.feature.toLowerCase()} (${topRisk?.actual_value}), qui augmente la probabilité de fraude de ${(topRisk?.contribution * 100).toFixed(1)}%. ${topProtective ? `Cependant, ${topProtective.feature.toLowerCase()} (${topProtective.actual_value}) réduit légèrement le risque.` : ''}`;
  } else {
    return `Cette transaction semble légitime. ${topProtective?.feature} (${topProtective?.actual_value}) contribue fortement à réduire le risque de fraude (${(Math.abs(topProtective?.contribution || 0) * 100).toFixed(1)}%). ${topRisk ? `Bien que ${topRisk.feature.toLowerCase()} augmente légèrement le risque, cela reste dans les normes.` : ''}`;
  }
};

// Mock data generator (à remplacer par vraie API)
const generateMockShapValues = (transaction: any): ExplanationData => {
  const fraudScore = transaction.fraud_score || 0.75;
  
  return {
    transaction_id: transaction.transaction_id,
    prediction: fraudScore,
    base_value: 0.15,
    confidence: 0.94,
    verdict: fraudScore > 0.7 ? 'fraud' : fraudScore > 0.4 ? 'suspicious' : 'legitimate',
    shap_values: [
      {
        feature: 'Montant Transaction',
        value: transaction.amount,
        actual_value: `${transaction.amount.toLocaleString()} XOF`,
        contribution: transaction.amount > 500000 ? 0.15 : -0.05,
        importance: transaction.amount > 500000 ? 'critical' : 'low',
        icon: DollarSign,
        description: transaction.amount > 500000 
          ? 'Montant exceptionnellement élevé, augmente fortement le risque'
          : 'Montant dans la norme pour ce type de transaction'
      },
      {
        feature: 'Heure de Transaction',
        value: new Date(transaction.timestamp).getHours(),
        actual_value: new Date(transaction.timestamp).toLocaleTimeString('fr-FR'),
        contribution: new Date(transaction.timestamp).getHours() < 6 ? 0.12 : -0.03,
        importance: new Date(transaction.timestamp).getHours() < 6 ? 'high' : 'low',
        icon: Clock,
        description: new Date(transaction.timestamp).getHours() < 6
          ? 'Transaction effectuée à une heure inhabituelle (nuit)'
          : 'Heure de transaction normale'
      },
      {
        feature: 'Type de Transaction',
        value: transaction.transaction_type,
        actual_value: transaction.transaction_type,
        contribution: transaction.transaction_type === 'cash_out' ? 0.08 : -0.02,
        importance: transaction.transaction_type === 'cash_out' ? 'high' : 'low',
        icon: Activity,
        description: transaction.transaction_type === 'cash_out'
          ? 'Les retraits sont plus à risque que les paiements'
          : 'Type de transaction standard'
      },
      {
        feature: 'Localisation',
        value: transaction.location,
        actual_value: transaction.location || 'Non spécifiée',
        contribution: !transaction.location ? 0.06 : -0.04,
        importance: !transaction.location ? 'medium' : 'low',
        icon: MapPin,
        description: !transaction.location
          ? 'Absence de localisation augmente le risque'
          : 'Localisation cohérente avec l\'historique'
      },
      {
        feature: 'Historique Client',
        value: transaction.customer_id,
        actual_value: transaction.customer_id,
        contribution: -0.08,
        importance: 'medium',
        icon: User,
        description: 'Client avec historique de transactions légitimes'
      },
      {
        feature: 'Appareil',
        value: transaction.device_id,
        actual_value: transaction.device_id || 'Non identifié',
        contribution: !transaction.device_id ? 0.05 : -0.03,
        importance: !transaction.device_id ? 'medium' : 'low',
        icon: Smartphone,
        description: !transaction.device_id
          ? 'Appareil non reconnu'
          : 'Appareil habituel du client'
      }
    ],
    risk_factors: [],
    protective_factors: []
  };
};

// ============================================================================
// DEMO APP
// ============================================================================

const DemoApp = () => {
  const mockTransaction = {
    transaction_id: 'TXN-2025-001',
    amount: 750000,
    customer_id: 'CUST-12345',
    transaction_type: 'cash_out',
    timestamp: new Date().toISOString(),
    location: 'Dakar, Sénégal',
    device_id: 'DEVICE-ABC123',
    fraud_score: 0.85,
    is_fraud: true
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🧠 SHAP Explainability Dashboard
          </h1>
          <p className="text-gray-600">
            Intelligence Artificielle Explicable pour la Détection de Fraude
          </p>
        </div>
        
        <ExplainabilityPanel transaction={mockTransaction} />
      </div>
    </div>
  );
};

export default DemoApp;