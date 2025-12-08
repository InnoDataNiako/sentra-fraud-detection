import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  Bell, 
  Clock, 
  Eye, 
  User, 
  MapPin, 
  DollarSign,
  CheckCircle,
  XCircle,
  MoreVertical,
  TrendingUp
} from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface Alert {
  id: string;
  transactionId: string;
  customerName: string;
  amount: number;
  location: string;
  riskScore: number;
  reason: string;
  timestamp: string;
  status: 'new' | 'investigating' | 'resolved' | 'false_positive';
  priority: 'low' | 'medium' | 'high' | 'critical';
  type: 'fraud_detected' | 'suspicious_pattern' | 'high_risk' | 'anomaly';
}

interface AlertFeedProps {
  alerts?: Alert[];
  onInvestigate?: (alertId: string) => void;
  onResolve?: (alertId: string, status: 'resolved' | 'false_positive') => void;
  loading?: boolean;
}

export const AlertFeed: React.FC<AlertFeedProps> = ({ 
  alerts = [], 
  onInvestigate, 
  onResolve,
  loading = false 
}) => {
  
  // Données d'exemple si pas d'alertes
  const defaultAlerts: Alert[] = [
    {
      id: 'alert_001',
      transactionId: 'txn_789123',
      customerName: 'Client ABC123',
      amount: 250000,
      location: 'Dakar, Sénégal',
      riskScore: 92,
      reason: 'Montant anormalement élevé pour ce client',
      timestamp: new Date().toISOString(),
      status: 'new',
      priority: 'high',
      type: 'fraud_detected'
    },
    {
      id: 'alert_002',
      transactionId: 'txn_456789',
      customerName: 'Client XYZ789',
      amount: 120000,
      location: 'Abidjan, Côte d\'Ivoire',
      riskScore: 85,
      reason: 'Localisation inhabituelle',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      status: 'investigating',
      priority: 'medium',
      type: 'suspicious_pattern'
    },
    {
      id: 'alert_003',
      transactionId: 'txn_123456',
      customerName: 'Client DEF456',
      amount: 75000,
      location: 'Lomé, Togo',
      riskScore: 78,
      reason: 'Transaction nocturne inhabituelle',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      status: 'new',
      priority: 'medium',
      type: 'anomaly'
    }
  ];

  const displayAlerts = alerts.length > 0 ? alerts : defaultAlerts;

  // Formatage
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR').format(amount) + ' F CFA';
  };

  const formatTime = (timestamp: string) => {
    return format(new Date(timestamp), 'HH:mm', { locale: fr });
  };

  const formatDate = (timestamp: string) => {
    return format(new Date(timestamp), 'dd MMM yyyy', { locale: fr });
  };

  // Couleurs et icônes selon la priorité
  const getPriorityConfig = (priority: Alert['priority']) => {
    switch (priority) {
      case 'critical':
        return {
          color: 'bg-red-100 text-red-800 border-red-200',
          icon: <AlertTriangle className="h-4 w-4" />,
          text: 'Critique'
        };
      case 'high':
        return {
          color: 'bg-orange-100 text-orange-800 border-orange-200',
          icon: <AlertTriangle className="h-4 w-4" />,
          text: 'Élevée'
        };
      case 'medium':
        return {
          color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: <Bell className="h-4 w-4" />,
          text: 'Moyenne'
        };
      case 'low':
        return {
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: <Bell className="h-4 w-4" />,
          text: 'Basse'
        };
    }
  };

  // Couleurs selon le statut
  const getStatusConfig = (status: Alert['status']) => {
    switch (status) {
      case 'new':
        return {
          color: 'bg-red-100 text-red-800',
          text: 'Nouveau'
        };
      case 'investigating':
        return {
          color: 'bg-yellow-100 text-yellow-800',
          text: 'En cours'
        };
      case 'resolved':
        return {
          color: 'bg-green-100 text-green-800',
          text: 'Résolu'
        };
      case 'false_positive':
        return {
          color: 'bg-gray-100 text-gray-800',
          text: 'Faux positif'
        };
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3
      }
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <Card key={i} className="animate-pulse">
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* En-tête */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          <h2 className="text-lg font-semibold">Alertes en temps réel</h2>
          <Badge variant="destructive" className="animate-pulse">
            {displayAlerts.length} active{displayAlerts.length > 1 ? 's' : ''}
          </Badge>
        </div>
        <Button variant="outline" size="sm">
          <TrendingUp className="h-4 w-4 mr-2" />
          Voir toutes les alertes
        </Button>
      </div>

      {/* Liste des alertes */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-4"
      >
        {displayAlerts.map((alert, index) => {
          const priorityConfig = getPriorityConfig(alert.priority);
          const statusConfig = getStatusConfig(alert.status);
          
          return (
            <motion.div key={alert.id} variants={itemVariants}>
              <Card className={`border-l-4 ${priorityConfig.color.split(' ')[0]} border-l-4`}>
                <CardContent className="pt-6">
                  {/* En-tête de l'alerte */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-full ${priorityConfig.color.split(' ')[0]}`}>
                        {priorityConfig.icon}
                      </div>
                      <div>
                        <h3 className="font-semibold">{alert.customerName}</h3>
                        <div className="flex items-center gap-3 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <DollarSign className="h-3 w-3" />
                            {formatCurrency(alert.amount)}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {alert.location}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {formatTime(alert.timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Badge variant="destructive" className="font-mono">
                        {alert.riskScore}%
                      </Badge>
                      <Badge className={priorityConfig.color}>
                        {priorityConfig.text}
                      </Badge>
                    </div>
                  </div>

                  {/* Détails de l'alerte */}
                  <div className="mb-4">
                    <p className="text-gray-700 mb-2">{alert.reason}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>Transaction: <strong>{alert.transactionId}</strong></span>
                      <span>Date: {formatDate(alert.timestamp)}</span>
                      <Badge className={statusConfig.color}>
                        {statusConfig.text}
                      </Badge>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex justify-between items-center pt-4 border-t">
                    <div className="flex items-center gap-2">
                      <Button 
                        size="sm" 
                        variant="default"
                        onClick={() => onInvestigate?.(alert.id)}
                        className="gap-2"
                      >
                        <Eye className="h-4 w-4" />
                        Investiguer
                      </Button>
                      
                      {alert.status === 'new' && (
                        <>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => onResolve?.(alert.id, 'false_positive')}
                            className="gap-2"
                          >
                            <XCircle className="h-4 w-4" />
                            Faux positif
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => onResolve?.(alert.id, 'resolved')}
                            className="gap-2"
                          >
                            <CheckCircle className="h-4 w-4" />
                            Résoudre
                          </Button>
                        </>
                      )}
                    </div>
                    
                    <Button variant="ghost" size="sm">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Message si pas d'alertes */}
      {displayAlerts.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">
              Aucune alerte active
            </h3>
            <p className="text-gray-500">
              Toutes les transactions sont normales pour le moment
            </p>
          </CardContent>
        </Card>
      )}

      {/* Statistiques */}
      <Card className="mt-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {displayAlerts.filter(a => a.priority === 'critical').length}
              </div>
              <div className="text-sm text-red-700">Critiques</div>
            </div>
            <div className="text-center p-3 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {displayAlerts.filter(a => a.priority === 'high').length}
              </div>
              <div className="text-sm text-orange-700">Élevées</div>
            </div>
            <div className="text-center p-3 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {displayAlerts.filter(a => a.status === 'investigating').length}
              </div>
              <div className="text-sm text-yellow-700">En investigation</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {displayAlerts.filter(a => a.status === 'resolved').length}
              </div>
              <div className="text-sm text-green-700">Résolues</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};