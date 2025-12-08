import React, { useState, useEffect } from 'react';
import { 
  Search, Filter, Download, ChevronLeft, ChevronRight, 
  Eye, AlertCircle, CheckCircle, TrendingUp, Calendar,
  FileText, Database, RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { fraudService } from '@/services/fraudService';
import { Transaction } from '@/types/fraud';
import { TransactionDetails } from '@/components/TransactionDetails';

interface TransactionFilters {
  search?: string;
  transaction_type?: string;
  is_fraud?: string;
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
}

export const History: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalTransactions, setTotalTransactions] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  
  // Filtres
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  
  // Transaction sélectionnée pour les détails
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  
  // Statistiques
  const [stats, setStats] = useState({
    total: 0,
    frauds: 0,
    totalAmount: 0,
    avgScore: 0,
  });

  // Charger les transactions
  const loadTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const queryParams = {
        ...filters,
        page: currentPage,
        page_size: pageSize,
      };
      
      const response = await fraudService.getTransactions(queryParams);
      
      setTransactions(response.items || []);
      setTotalTransactions(response.total || 0);
      setTotalPages(response.pages || 1);
      
      // Calculer les statistiques
      const frauds = response.items?.filter(t => t.is_fraud).length || 0;
      const totalAmount = response.items?.reduce((sum, t) => sum + t.amount, 0) || 0;
      const avgScore = response.items?.reduce((sum, t) => sum + t.fraud_score, 0) || 0 / (response.items?.length || 1);
      
      setStats({
        total: response.total || 0,
        frauds,
        totalAmount,
        avgScore: avgScore * 100,
      });
      
    } catch (err) {
      console.error('Erreur chargement historique:', err);
      setError('Impossible de charger les transactions');
    } finally {
      setLoading(false);
    }
  };

  // Chargement initial
  useEffect(() => {
    loadTransactions();
  }, [currentPage, pageSize, filters]);

  // Gestion des filtres
  const handleFilterChange = (key: keyof TransactionFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Retour à la première page
  };

  const clearFilters = () => {
    setFilters({});
    setCurrentPage(1);
  };

  // Formateurs
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount) + ' XOF';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1) + '%';
  };

  // Badge de statut
  const StatusBadge = ({ isFraud, score }: { isFraud: boolean; score: number }) => {
    if (isFraud) {
      return (
        <Badge variant="destructive" className="gap-1">
          <AlertCircle className="h-3 w-3" />
          Fraude
        </Badge>
      );
    }
    
    if (score > 0.7) {
      return (
        <Badge variant="secondary" className="gap-1 bg-red-100 text-red-800 border-red-300">
          <AlertCircle className="h-3 w-3" />
          Haut risque
        </Badge>
      );
    }
    
    if (score > 0.4) {
      return (
        <Badge variant="secondary" className="gap-1 bg-orange-100 text-orange-800 border-orange-300">
          <AlertCircle className="h-3 w-3" />
          Risque moyen
        </Badge>
      );
    }
    
    return (
      <Badge variant="secondary" className="gap-1 bg-green-100 text-green-800 border-green-300">
        <CheckCircle className="h-3 w-3" />
        Faible risque
      </Badge>
    );
  };

  // Export CSV
  const exportToCSV = () => {
    const headers = [
      'ID Transaction',
      'Client',
      'Montant',
      'Type',
      'Date',
      'Score Fraude',
      'Statut',
      'Localisation'
    ];
    
    const csvData = transactions.map(t => [
      t.transaction_id,
      t.customer_id,
      t.amount,
      t.transaction_type,
      new Date(t.timestamp).toISOString(),
      t.fraud_score,
      t.is_fraud ? 'Fraude' : 'Légitime',
      t.location || ''
    ]);
    
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `transactions-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (loading && transactions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <RefreshCw className="h-12 w-12 animate-spin text-blue-600 mb-4" />
        <p className="text-lg font-semibold text-gray-700">Chargement de l'historique</p>
        <p className="text-sm text-gray-500 mt-2">
          Récupération de {totalTransactions} transactions...
        </p>
      </div>
    );
  }

  if (error && transactions.length === 0) {
    return (
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Historique des Transactions</h1>
          <p className="text-gray-500 mt-1">Toutes les transactions analysées par SÉNTRA</p>
        </div>
        
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-red-800 mb-2">Erreur de chargement</h3>
              <p className="text-red-600 mb-4">{error}</p>
              <Button onClick={loadTransactions} variant="outline" className="mt-4">
                <RefreshCw className="h-4 w-4 mr-2" />
                Réessayer
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
      {/* En-tête */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              📜 Historique des Transactions
            </h1>
            <div className="flex flex-wrap items-center gap-3">
              <p className="text-gray-600">
                Archive complète de toutes les transactions analysées
              </p>
              <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300">
                <Database className="h-3 w-3 mr-1" />
                {totalTransactions.toLocaleString('fr-FR')} transactions
              </Badge>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={loadTransactions}
              disabled={loading}
              variant="outline"
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Actualiser
            </Button>
            <Button onClick={exportToCSV} className="gap-2 bg-green-600 hover:bg-green-700">
              <Download className="h-4 w-4" />
              Exporter CSV
            </Button>
          </div>
        </div>
      </div>

      {/* Cartes de statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium">Total Transactions</p>
                <p className="text-2xl font-bold mt-1">{stats.total.toLocaleString('fr-FR')}</p>
              </div>
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium">Fraudes Détectées</p>
                <p className="text-2xl font-bold text-red-600 mt-1">
                  {stats.frauds.toLocaleString('fr-FR')}
                </p>
              </div>
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium">Montant Total</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {formatAmount(stats.totalAmount)}
                </p>
              </div>
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium">Score Moyen</p>
                <p className="text-2xl font-bold mt-1">{stats.avgScore.toFixed(1)}%</p>
              </div>
              <div className="p-2 bg-orange-100 rounded-lg">
                <AlertCircle className="h-5 w-5 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Barre de recherche et filtres */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Barre de recherche */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Rechercher par ID transaction, client..."
                    value={filters.search || ''}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              {/* Boutons filtres */}
              <div className="flex gap-2">
                <Button
                  variant={showFilters ? "default" : "outline"}
                  onClick={() => setShowFilters(!showFilters)}
                  className="gap-2"
                >
                  <Filter className="h-4 w-4" />
                  Filtres {Object.keys(filters).length > 0 && `(${Object.keys(filters).length})`}
                </Button>
                
                {Object.keys(filters).length > 0 && (
                  <Button variant="ghost" onClick={clearFilters} className="text-red-600">
                    Effacer les filtres
                  </Button>
                )}
              </div>
            </div>

            {/* Filtres avancés */}
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg border">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Type</label>
                  <Select
                    value={filters.transaction_type || ''}
                    onValueChange={(value) => handleFilterChange('transaction_type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Tous les types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Tous les types</SelectItem>
                      <SelectItem value="cash_in">Cash-in</SelectItem>
                      <SelectItem value="cash_out">Cash-out</SelectItem>
                      <SelectItem value="transfer">Transfert</SelectItem>
                      <SelectItem value="payment">Paiement</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Statut</label>
                  <Select
                    value={filters.is_fraud || ''}
                    onValueChange={(value) => handleFilterChange('is_fraud', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Tous les statuts" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Tous les statuts</SelectItem>
                      <SelectItem value="true">Fraude seulement</SelectItem>
                      <SelectItem value="false">Légitime seulement</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Date de début</label>
                  <Input
                    type="date"
                    value={filters.start_date || ''}
                    onChange={(e) => handleFilterChange('start_date', e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Date de fin</label>
                  <Input
                    type="date"
                    value={filters.end_date || ''}
                    onChange={(e) => handleFilterChange('end_date', e.target.value)}
                  />
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tableau des transactions */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              Tableau des Transactions
            </CardTitle>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-600">
                Affichage {((currentPage - 1) * pageSize) + 1}-
                {Math.min(currentPage * pageSize, totalTransactions)} sur {totalTransactions}
              </div>
              <Select
                value={pageSize.toString()}
                onValueChange={(value) => {
                  setPageSize(parseInt(value));
                  setCurrentPage(1);
                }}
              >
                <SelectTrigger className="w-24">
                  <SelectValue placeholder="50" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="25">25</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border overflow-hidden">
            <Table>
              <TableHeader className="bg-gray-50">
                <TableRow>
                  <TableHead className="font-semibold">ID Transaction</TableHead>
                  <TableHead className="font-semibold">Client</TableHead>
                  <TableHead className="font-semibold">Montant</TableHead>
                  <TableHead className="font-semibold">Type</TableHead>
                  <TableHead className="font-semibold">Date</TableHead>
                  <TableHead className="font-semibold">Score Fraude</TableHead>
                  <TableHead className="font-semibold">Statut</TableHead>
                  <TableHead className="font-semibold text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((transaction) => (
                  <TableRow key={transaction.id} className="hover:bg-gray-50">
                    <TableCell className="font-mono text-sm">
                      {transaction.transaction_id}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-medium">{transaction.customer_id}</span>
                        {transaction.location && (
                          <span className="text-xs text-gray-500">{transaction.location}</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="font-semibold">
                      {formatAmount(transaction.amount)}
                    </TableCell>
                    <TableCell>
                      <span className="capitalize text-sm">
                        {transaction.transaction_type}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(transaction.timestamp)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className={`font-medium ${
                          transaction.fraud_score > 0.7 ? 'text-red-600' :
                          transaction.fraud_score > 0.4 ? 'text-orange-600' :
                          transaction.fraud_score > 0.2 ? 'text-yellow-600' :
                          'text-green-600'
                        }`}>
                          {formatScore(transaction.fraud_score)}
                        </span>
                        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${
                              transaction.fraud_score > 0.7 ? 'bg-red-500' :
                              transaction.fraud_score > 0.4 ? 'bg-orange-500' :
                              transaction.fraud_score > 0.2 ? 'bg-yellow-500' :
                              'bg-green-500'
                            }`}
                            style={{ width: `${transaction.fraud_score * 100}%` }}
                          />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge 
                        isFraud={transaction.is_fraud} 
                        score={transaction.fraud_score} 
                      />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedTransaction(transaction)}
                        className="gap-1"
                      >
                        <Eye className="h-4 w-4" />
                        Détails
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-600">
                Page {currentPage} sur {totalPages}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Précédent
                </Button>
                
                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? "default" : "outline"}
                        size="sm"
                        onClick={() => setCurrentPage(pageNum)}
                        className="h-8 w-8 p-0"
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  Suivant
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modale de détails */}
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