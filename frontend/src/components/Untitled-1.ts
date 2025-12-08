


// import React, { useState, useEffect, useRef } from 'react';
// import { 
//   Activity, 
//   AlertTriangle, 
//   DollarSign, 
//   Shield, 
//   RefreshCw, 
//   TrendingUp, 
//   TrendingDown,
//   Clock,
//   Users,
//   MapPin,
//   BarChart3,
//   Bell,
//   Download,
//   Filter,
//   ChevronRight
// } from 'lucide-react';
// import { motion, AnimatePresence } from 'framer-motion';
// import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
// import { Button } from '@/components/ui/button';
// import { Badge } from '@/components/ui/badge';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { Progress } from '@/components/ui/progress';
// import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
// import { fraudService } from '@/services/fraudService';
// import { useMetrics, useWebSocket } from '@/hooks';
// import { Transaction } from '@/types/fraud';
// import { RecentTransactions } from '@/components/RecentTransactions';
// import { TransactionDetails } from '@/components/TransactionDetails';
// import { LiveTransactionFeed } from '@/components/LiveTransactionFeed';
// import { FraudChart } from '@/components/FraudChart';
// import { AlertFeed } from '@/components/AlertFeed';
// import { RiskMap } from '@/components/RiskMap';

// // Types pour les données en temps réel
// interface LiveTransaction {
//   id: string;
//   amount: number;
//   customerName: string;
//   location: string;
//   riskScore: number;
//   timestamp: string;
//   status: 'approved' | 'blocked' | 'pending';
// }

// export const Dashboard: React.FC = () => {
//   // 🔧 Données principales
//   const { metrics, loading: metricsLoading, error: metricsError, refresh: refreshMetrics } = useMetrics();
  
//   // 🔧 États améliorés
//   const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
//   const [liveTransactions, setLiveTransactions] = useState<LiveTransaction[]>([]);
//   const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
//   const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'alerts'>('overview');
//   const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');
//   const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
//   const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
//   const transactionsLoading = useRef(false);

//   // 🔧 WebSocket pour les transactions en temps réel
//   const { data: wsData, isConnected } = useWebSocket('ws://localhost:8000/ws/transactions');

//   // 🔧 Effet pour WebSocket
//   useEffect(() => {
//     if (wsData) {
//       const transaction = JSON.parse(wsData);
//       setLiveTransactions(prev => [transaction, ...prev.slice(0, 9)]);
      
//       // Notification si risque élevé
//       if (transaction.riskScore > 70) {
//         showNotification(`🚨 Transaction suspecte détectée: ${transaction.amount} F CFA`);
//       }
//     }
//   }, [wsData]);

//   // 🔧 Chargement des transactions
//   const loadTransactions = async () => {
//     if (transactionsLoading.current) return;
    
//     try {
//       transactionsLoading.current = true;
//       const transactionsData = await fraudService.getTransactions({}, { page_size: 10 });
//       setRecentTransactions(transactionsData.items || []);
//       setLastUpdate(new Date());
//     } catch (err) {
//       console.error('Erreur chargement transactions:', err);
//     } finally {
//       transactionsLoading.current = false;
//     }
//   };

//   // 🔧 Configuration de l'auto-refresh
//   useEffect(() => {
//     loadTransactions();
    
//     // Auto-refresh toutes les 30 secondes
//     const interval = setInterval(() => {
//       if (!transactionsLoading.current) {
//         loadTransactions();
//         refreshMetrics();
//       }
//     }, 30000);
    
//     setRefreshInterval(interval);
    
//     return () => {
//       if (refreshInterval) clearInterval(refreshInterval);
//     };
//   }, []);

//   // 🔧 Notification toast
//   const showNotification = (message: string) => {
//     if ('Notification' in window && Notification.permission === 'granted') {
//       new Notification('🚨 Alerte SÉNTRA', {
//         body: message,
//         icon: '/favicon.ico'
//       });
//     }
//   };

//   // 🔧 Fonctions de gestion
//   const handleViewDetails = (transaction: Transaction) => {
//     setSelectedTransaction(transaction);
//   };

//   const handleCloseDetails = () => {
//     setSelectedTransaction(null);
//   };

//   const handleRefresh = () => {
//     refreshMetrics();
//     loadTransactions();
//   };

//   const handleExport = () => {
//     // Exporter les données du dashboard
//     const exportData = {
//       metrics,
//       timestamp: new Date().toISOString(),
//       transactions: recentTransactions
//     };
    
//     const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
//     const url = URL.createObjectURL(blob);
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = `sentra-dashboard-${new Date().toISOString().split('T')[0]}.json`;
//     a.click();
//   };

//   // 🔧 Formatage
//   const formatNumber = (num: number | undefined): string => {
//     if (num === undefined || num === null) return '0';
//     return new Intl.NumberFormat('fr-FR').format(num);
//   };

//   const formatCurrency = (amount: number | undefined): string => {
//     if (amount === undefined || amount === null) return '0 F CFA';
//     return new Intl.NumberFormat('fr-FR', {
//       minimumFractionDigits: 0,
//       maximumFractionDigits: 0,
//     }).format(amount) + ' F CFA';
//   };

//   const formatTime = (date: Date) => {
//     return date.toLocaleTimeString('fr-FR', { 
//       hour: '2-digit', 
//       minute: '2-digit',
//       second: '2-digit'
//     });
//   };

//   // 🔧 États combinés
//   const isLoading = metricsLoading && !metrics;
//   const hasError = metricsError && !metrics;
//   const loading = metricsLoading;

//   // 🔧 Calculs dérivés
//   const fraudTrend = metrics ? (metrics.fraud_rate || 0) > 2.5 ? 'up' : 'down' : 'stable';
//   const avgRiskScore = metrics ? (metrics.total_risk_score || 0) / (metrics.total_transactions || 1) : 0;

//   // 🔧 Animation variants
//   const cardVariants = {
//     hidden: { opacity: 0, y: 20 },
//     visible: { 
//       opacity: 1, 
//       y: 0,
//       transition: { duration: 0.3 }
//     }
//   };
//   // Ajoute cette fonction pour formater les données
// const formatChartData = () => {
//   if (!recentTransactions.length) return { trendData: [], amountDistribution: [] };
  
//   // Simuler des données de tendance (à remplacer par vraies données API)
//   const trendData = Array.from({ length: 30 }, (_, i) => {
//     const date = new Date();
//     date.setDate(date.getDate() - (29 - i));
//     return {
//       date: date.toISOString(),
//       total: Math.floor(Math.random() * 500) + 400,
//       fraud: Math.floor(Math.random() * 15) + 5,
//       fraudRate: (Math.random() * 2 + 1.5)
//     };
//   });
  
//   // Distribution des montants
//   const amountDistribution = [
//     { range: '0-10k', count: Math.floor(Math.random() * 300) + 200, fraud_count: Math.floor(Math.random() * 10) + 2 },
//     { range: '10k-50k', count: Math.floor(Math.random() * 200) + 150, fraud_count: Math.floor(Math.random() * 8) + 3 },
//     { range: '50k-100k', count: Math.floor(Math.random() * 100) + 50, fraud_count: Math.floor(Math.random() * 6) + 4 },
//     { range: '100k-500k', count: Math.floor(Math.random() * 50) + 20, fraud_count: Math.floor(Math.random() * 4) + 3 },
//     { range: '500k+', count: Math.floor(Math.random() * 20) + 5, fraud_count: Math.floor(Math.random() * 3) + 2 },
//   ];
  
//   // Niveaux de risque
//   const riskLevelData = [
//     { name: 'Faible (<30%)', value: Math.floor(Math.random() * 400) + 300, color: '#10b981' },
//     { name: 'Moyen (30-70%)', value: Math.floor(Math.random() * 150) + 100, color: '#f59e0b' },
//     { name: 'Élevé (>70%)', value: Math.floor(Math.random() * 50) + 20, color: '#ef4444' },
//   ];
  
//   // Types de transaction
//   const transactionTypeData = [
//     { type: 'Payment', total: 350, fraud: 12 },
//     { type: 'Transfer', total: 280, fraud: 15 },
//     { type: 'Withdrawal', total: 220, fraud: 8 },
//     { type: 'Cash In', total: 180, fraud: 5 },
//     { type: 'Bill', total: 120, fraud: 4 },
//   ];
  
//   return { trendData, amountDistribution, riskLevelData, transactionTypeData };
// };

//   if (isLoading) {
//     return (
//       <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
//         <motion.div
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           className="text-center space-y-6"
//         >
//           <div className="relative">
//             <Shield className="h-16 w-16 text-blue-600 mx-auto mb-4" />
//             <RefreshCw className="absolute top-1/2 left-1/2 h-20 w-20 -translate-x-1/2 -translate-y-1/2 animate-spin text-blue-200" />
//           </div>
//           <div>
//             <h2 className="text-2xl font-bold text-gray-900 mb-2">Initialisation du Dashboard</h2>
//             <p className="text-gray-600">Connexion aux services SÉNTRA...</p>
//             <Progress value={60} className="w-64 mx-auto mt-4" />
//           </div>
//         </motion.div>
//       </div>
//     );
//   }

//   if (hasError) {
//     return (
//       <motion.div 
//         initial={{ opacity: 0 }}
//         animate={{ opacity: 1 }}
//         className="space-y-6 p-6"
//       >
//         <Card className="border-red-200 bg-gradient-to-r from-red-50 to-orange-50 shadow-lg">
//           <CardContent className="pt-8 pb-8">
//             <div className="text-center max-w-2xl mx-auto">
//               <motion.div
//                 animate={{ scale: [1, 1.1, 1] }}
//                 transition={{ repeat: Infinity, duration: 2 }}
//               >
//                 <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
//               </motion.div>
//               <h3 className="text-2xl font-bold text-red-800 mb-3">Connexion au backend échouée</h3>
//               <p className="text-red-600 mb-6">{metricsError}</p>
              
//               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left mb-6">
//                 <div className="bg-white p-4 rounded-lg shadow">
//                   <h4 className="font-semibold mb-2">🔍 Vérifications requises</h4>
//                   <ul className="space-y-1 text-sm">
//                     <li className="flex items-center gap-2">
//                       <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
//                       Backend démarré (port 8000)
//                     </li>
//                     <li className="flex items-center gap-2">
//                       <div className="h-2 w-2 rounded-full bg-gray-300" />
//                       PostgreSQL accessible
//                     </li>
//                     <li className="flex items-center gap-2">
//                       <div className="h-2 w-2 rounded-full bg-gray-300" />
//                       API fonctionnelle
//                     </li>
//                   </ul>
//                 </div>
                
//                 <div className="bg-white p-4 rounded-lg shadow">
//                   <h4 className="font-semibold mb-2">🚀 Actions rapides</h4>
//                   <ul className="space-y-1 text-sm">
//                     <li>1. Vérifiez docker-compose</li>
//                     <li>2. Consultez les logs backend</li>
//                     <li>3. Testez l'API avec curl</li>
//                   </ul>
//                 </div>
//               </div>
              
//               <Button onClick={handleRefresh} size="lg" className="gap-2">
//                 <RefreshCw className="h-4 w-4" />
//                 Réessayer la connexion
//               </Button>
//             </div>
//           </CardContent>
//         </Card>
//       </motion.div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
//       {/* Header avec status en temps réel */}
//       <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-sm border-b">
//         <div className="px-6 py-4">
//           <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
//             <div>
//               <div className="flex items-center gap-3">
//                 <Shield className="h-8 w-8 text-blue-600" />
//                 <div>
//                   <h1 className="text-2xl font-bold text-gray-900">Dashboard SÉNTRA</h1>
//                   <div className="flex items-center gap-3 mt-1">
//                     <Badge variant={isConnected ? "default" : "destructive"} className="gap-1">
//                       <div className={`h-2 w-2 rounded-full ${isConnected ? 'animate-pulse bg-green-400' : 'bg-red-400'}`} />
//                       {isConnected ? 'Connecté en temps réel' : 'Hors ligne'}
//                     </Badge>
//                     <span className="text-sm text-gray-500">
//                       Dernière mise à jour: {formatTime(lastUpdate)}
//                     </span>
//                   </div>
//                 </div>
//               </div>
//             </div>
            
//             <div className="flex items-center gap-2">
//               <TooltipProvider>
//                 <Tooltip>
//                   <TooltipTrigger asChild>
//                     <Button variant="outline" size="sm" onClick={handleExport}>
//                       <Download className="h-4 w-4" />
//                     </Button>
//                   </TooltipTrigger>
//                   <TooltipContent>Exporter les données</TooltipContent>
//                 </Tooltip>
//               </TooltipProvider>
              
//               <TooltipProvider>
//                 <Tooltip>
//                   <TooltipTrigger asChild>
//                     <Button variant="outline" size="sm" onClick={handleRefresh} disabled={loading}>
//                       <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
//                     </Button>
//                   </TooltipTrigger>
//                   <TooltipContent>Actualiser manuellement</TooltipContent>
//                 </Tooltip>
//               </TooltipProvider>
              
//               <Button onClick={() => setActiveTab('alerts')} variant="outline" size="sm" className="relative">
//                 <Bell className="h-4 w-4" />
//                 {liveTransactions.filter(t => t.riskScore > 70).length > 0 && (
//                   <span className="absolute -top-1 -right-1 h-2 w-2 bg-red-500 rounded-full"></span>
//                 )}
//               </Button>
//             </div>
//           </div>
//         </div>
//       </div>

//       {/* Contenu principal */}
//       <div className="p-6 space-y-6">
//         {/* Filtres et contrôles */}
//         <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
//           <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
//             <TabsList>
//               <TabsTrigger value="overview" className="gap-2">
//                 <Activity className="h-4 w-4" />
//                 Vue d'ensemble
//               </TabsTrigger>
//               <TabsTrigger value="analytics" className="gap-2">
//                 <BarChart3 className="h-4 w-4" />
//                 Analytics
//               </TabsTrigger>
//               <TabsTrigger value="alerts" className="gap-2">
//                 <AlertTriangle className="h-4 w-4" />
//                 Alertes
//                 {liveTransactions.filter(t => t.riskScore > 70).length > 0 && (
//                   <Badge variant="destructive" className="ml-1 h-5 w-5 p-0">
//                     {liveTransactions.filter(t => t.riskScore > 70).length}
//                   </Badge>
//                 )}
//               </TabsTrigger>
//             </TabsList>
//           </Tabs>
          
//           <div className="flex items-center gap-2">
//             <Tabs value={timeRange} onValueChange={(v: any) => setTimeRange(v)}>
//               <TabsList>
//                 <TabsTrigger value="24h">24h</TabsTrigger>
//                 <TabsTrigger value="7d">7j</TabsTrigger>
//                 <TabsTrigger value="30d">30j</TabsTrigger>
//               </TabsList>
//             </Tabs>
//             <Button variant="outline" size="sm">
//               <Filter className="h-4 w-4 mr-2" />
//               Filtres
//             </Button>
//           </div>
//         </div>

//         {/* Vue d'ensemble */}
//         {activeTab === 'overview' && (
//           <AnimatePresence>
//             <motion.div
//               initial={{ opacity: 0 }}
//               animate={{ opacity: 1 }}
//               exit={{ opacity: 0 }}
//               className="space-y-6"
//             >
//               {/* Cartes de métriques avec animations */}
//               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//                 {metrics && (
//                   <>
//                     <motion.div variants={cardVariants} initial="hidden" animate="visible">
//                       <Card className="hover:shadow-lg transition-shadow duration-300 border-blue-100">
//                         <CardHeader className="pb-3">
//                           <div className="flex justify-between items-center">
//                             <CardTitle className="text-sm font-medium text-gray-600">
//                               Transactions Total
//                             </CardTitle>
//                             <Activity className="h-5 w-5 text-blue-500" />
//                           </div>
//                         </CardHeader>
//                         <CardContent>
//                           <div className="text-3xl font-bold text-gray-900">
//                             {formatNumber(metrics.total_transactions)}
//                           </div>
//                           <div className="flex items-center gap-2 mt-2">
//                             <TrendingUp className="h-4 w-4 text-green-500" />
//                             <span className="text-sm text-green-600">+12% vs période précédente</span>
//                           </div>
//                           <Progress value={85} className="mt-3" />
//                         </CardContent>
//                       </Card>
//                     </motion.div>

//                     <motion.div variants={cardVariants} initial="hidden" animate="visible" transition={{ delay: 0.1 }}>
//                       <Card className="hover:shadow-lg transition-shadow duration-300 border-red-100">
//                         <CardHeader className="pb-3">
//                           <div className="flex justify-between items-center">
//                             <CardTitle className="text-sm font-medium text-gray-600">
//                               Fraudes Détectées
//                             </CardTitle>
//                             <AlertTriangle className="h-5 w-5 text-red-500" />
//                           </div>
//                         </CardHeader>
//                         <CardContent>
//                           <div className="text-3xl font-bold text-red-600">
//                             {formatNumber(metrics.frauds_detected)}
//                           </div>
//                           <div className="flex items-center gap-2 mt-2">
//                             {fraudTrend === 'up' ? (
//                               <TrendingUp className="h-4 w-4 text-red-500" />
//                             ) : (
//                               <TrendingDown className="h-4 w-4 text-green-500" />
//                             )}
//                             <span className={`text-sm ${fraudTrend === 'up' ? 'text-red-600' : 'text-green-600'}`}>
//                               Taux: {(metrics.fraud_rate || 0).toFixed(2)}%
//                             </span>
//                           </div>
//                           <div className="text-xs text-gray-500 mt-1">
//                             Seuil: 2.8% (moyenne BCEAO)
//                           </div>
//                         </CardContent>
//                       </Card>
//                     </motion.div>

//                     <motion.div variants={cardVariants} initial="hidden" animate="visible" transition={{ delay: 0.2 }}>
//                       <Card className="hover:shadow-lg transition-shadow duration-300 border-green-100">
//                         <CardHeader className="pb-3">
//                           <div className="flex justify-between items-center">
//                             <CardTitle className="text-sm font-medium text-gray-600">
//                               Montant Protégé
//                             </CardTitle>
//                             <DollarSign className="h-5 w-5 text-green-500" />
//                           </div>
//                         </CardHeader>
//                         <CardContent>
//                           <div className="text-3xl font-bold text-green-700">
//                             {formatCurrency(metrics.blocked_amount)}
//                           </div>
//                           <div className="text-sm text-gray-600 mt-2">
//                             Économies réalisées
//                           </div>
//                           <Badge variant="outline" className="mt-2">
//                             +5.2M XOF aujourd'hui
//                           </Badge>
//                         </CardContent>
//                       </Card>
//                     </motion.div>

//                     <motion.div variants={cardVariants} initial="hidden" animate="visible" transition={{ delay: 0.3 }}>
//                       <Card className="hover:shadow-lg transition-shadow duration-300 border-purple-100">
//                         <CardHeader className="pb-3">
//                           <div className="flex justify-between items-center">
//                             <CardTitle className="text-sm font-medium text-gray-600">
//                               Performance
//                             </CardTitle>
//                             <Shield className="h-5 w-5 text-purple-500" />
//                           </div>
//                         </CardHeader>
//                         <CardContent>
//                           <div className="text-3xl font-bold text-purple-700">
//                             {((metrics.model_accuracy || 0) * 100).toFixed(1)}%
//                           </div>
//                           <div className="flex items-center justify-between mt-2">
//                             <div className="text-sm text-gray-600">
//                               Score de risque moyen
//                             </div>
//                             <Badge variant={avgRiskScore > 50 ? "destructive" : "default"}>
//                               {avgRiskScore.toFixed(1)}%
//                             </Badge>
//                           </div>
//                           <div className="text-xs text-gray-500 mt-1">
//                             Temps: {(metrics.avg_processing_time_ms || 0).toFixed(0)}ms
//                           </div>
//                         </CardContent>
//                       </Card>
//                     </motion.div>
//                   </>
//                 )}
//               </div>

//               {/* Graphiques et visualisations */}
//               <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//                 <Card className="lg:col-span-2">
//                   <CardHeader>
//                     <CardTitle>Tendances des fraudes</CardTitle>
//                     <CardDescription>Évolution sur les 30 derniers jours</CardDescription>
//                   </CardHeader>
//                   <CardContent>
//                     <FraudChart timeRange={timeRange} />
//                   </CardContent>
//                 </Card>

//                 <Card>
//                   <CardHeader>
//                     <CardTitle>Transactions en temps réel</CardTitle>
//                     <CardDescription>Dernières activités</CardDescription>
//                   </CardHeader>
//                   <CardContent>
//                     <LiveTransactionFeed transactions={liveTransactions} />
//                   </CardContent>
//                 </Card>
//               </div>

//               {/* Carte géographique et transactions */}
//               <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//                 <Card className="lg:col-span-2">
//                   <CardHeader>
//                     <CardTitle>Carte des risques géographiques</CardTitle>
//                     <CardDescription>Localisation des fraudes détectées</CardDescription>
//                   </CardHeader>
//                   <CardContent className="h-[300px]">
//                     <RiskMap transactions={recentTransactions} />
//                   </CardContent>
//                 </Card>

//                 <Card>
//                   <CardHeader>
//                     <CardTitle>Top clients à risque</CardTitle>
//                     <CardDescription>Suivi proactif</CardDescription>
//                   </CardHeader>
//                   <CardContent>
//                     <div className="space-y-4">
//                       {recentTransactions
//                         .filter(t => t.risk_score > 70)
//                         .slice(0, 3)
//                         .map((transaction, index) => (
//                           <div key={transaction.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
//                             <div className="flex items-center gap-3">
//                               <Users className="h-5 w-5 text-red-500" />
//                               <div>
//                                 <div className="font-medium">Client {transaction.customer_id}</div>
//                                 <div className="text-sm text-gray-500">{formatCurrency(transaction.amount)}</div>
//                               </div>
//                             </div>
//                             <Badge variant="destructive">{transaction.risk_score}%</Badge>
//                           </div>
//                         ))}
//                     </div>
//                   </CardContent>
//                 </Card>
//               </div>

//               {/* Transactions récentes */}
//               <RecentTransactions 
//                 transactions={recentTransactions} 
//                 onViewDetails={handleViewDetails}  
//               />
//             </motion.div>
//           </AnimatePresence>
//         )}

//         {/* Analytics */}
//         {activeTab === 'analytics' && (
//           <motion.div
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             className="space-y-6"
//           >
//             {/* Contenu analytics */}
//             <Card>
//               <CardHeader>
//                 <CardTitle>Analytics avancés</CardTitle>
//                 <CardDescription>Analyse détaillée des patterns de fraude</CardDescription>
//               </CardHeader>
//               <CardContent>
//                 <div className="h-[400px] flex items-center justify-center border-2 border-dashed border-gray-200 rounded-lg">
//                   <div className="text-center">
//                     <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
//                     <p className="text-gray-500">Dashboard analytics en cours de développement</p>
//                     <Button variant="outline" className="mt-4">
//                       Configurer les rapports
//                     </Button>
//                   </div>
//                 </div>
//               </CardContent>
//             </Card>
//           </motion.div>
//         )}

//         {/* Alertes */}
//         {activeTab === 'alerts' && (
//           <motion.div
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             className="space-y-6"
//           >
//             <AlertFeed 
//               transactions={liveTransactions.filter(t => t.riskScore > 70)} 
//               onInvestigate={(id) => console.log('Investigate:', id)}
//             />
//           </motion.div>
//         )}
//       </div>

//       {/* Modale de détails */}
//       {selectedTransaction && (
//         <TransactionDetails
//           transaction={selectedTransaction}
//           isOpen={!!selectedTransaction}
//           onClose={handleCloseDetails}
//         />
//       )}

//       {/* Footer avec statistiques */}
//       <div className="mt-8 px-6 py-4 border-t bg-gray-50">
//         <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600">
//           <div className="flex items-center gap-6">
//             <div className="flex items-center gap-2">
//               <div className="h-2 w-2 rounded-full bg-green-500"></div>
//               <span>Transactions normales: {recentTransactions.filter(t => t.risk_score < 30).length}</span>
//             </div>
//             <div className="flex items-center gap-2">
//               <div className="h-2 w-2 rounded-full bg-yellow-500"></div>
//               <span>À surveiller: {recentTransactions.filter(t => t.risk_score >= 30 && t.risk_score <= 70).length}</span>
//             </div>
//             <div className="flex items-center gap-2">
//               <div className="h-2 w-2 rounded-full bg-red-500"></div>
//               <span>Critiques: {recentTransactions.filter(t => t.risk_score > 70).length}</span>
//             </div>
//           </div>
//           <div className="mt-2 sm:mt-0">
//             <span className="text-gray-500">SÉNTRA v1.0 • Système de détection de fraude BCEAO 2023</span>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };