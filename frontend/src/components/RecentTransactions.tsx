
/**
 * Tableau des transactions récentes
 * Affiche les dernières transactions avec statut et détails
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  TrendingUp,
  Eye,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { Transaction } from '@/types/fraud';

interface RecentTransactionsProps {
  transactions: Transaction[];
  onViewDetails?: (transaction: Transaction) => void;
}

export const RecentTransactions: React.FC<RecentTransactionsProps> = ({
  transactions,
  onViewDetails,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Pagination
  const totalPages = Math.ceil(transactions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentTransactions = transactions.slice(startIndex, endIndex);

  // Formater la date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Formater le montant
  const formatAmount = (amount: number, currency: string = 'XOF') => {
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount) + ` ${currency}`;
  };

  // Badge de statut
  const StatusBadge = ({ isFraud, fraudScore }: { isFraud: boolean; fraudScore: number }) => {
    if (isFraud) {
      return (
        <Badge variant="destructive" className="gap-1">
          <AlertCircle className="h-3 w-3" />
          Fraude
        </Badge>
      );
    }
    
    if (fraudScore > 0.5) {
      return (
        <Badge variant="secondary" className="gap-1 bg-orange-100 text-orange-800 border-orange-300">
          <AlertCircle className="h-3 w-3" />
          Suspect
        </Badge>
      );
    }
    
    return (
      <Badge variant="secondary" className="gap-1 bg-green-100 text-green-800 border-green-300">
        <CheckCircle className="h-3 w-3" />
        Légitime
      </Badge>
    );
  };

  // Score de fraude coloré
  const FraudScoreCell = ({ score }: { score: number }) => {
    const percentage = (score * 100).toFixed(1);
    let colorClass = 'text-green-600';
    
    if (score > 0.7) colorClass = 'text-red-600';
    else if (score > 0.4) colorClass = 'text-orange-600';
    else if (score > 0.2) colorClass = 'text-yellow-600';
    
    return (
      <div className="flex items-center gap-2">
        <span className={`font-medium ${colorClass}`}>{percentage}%</span>
        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full ${
              score > 0.7 ? 'bg-red-500' : 
              score > 0.4 ? 'bg-orange-500' : 
              score > 0.2 ? 'bg-yellow-500' : 
              'bg-green-500'
            }`}
            style={{ width: `${score * 100}%` }}
          />
        </div>
      </div>
    );
  };

  if (transactions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-blue-600" />
            Transactions Récentes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-gray-500">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium">Aucune transaction à afficher</p>
            <p className="text-sm mt-2">Les transactions apparaîtront ici une fois analysées</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-blue-600" />
            Transactions Récentes
          </CardTitle>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <TrendingUp className="h-4 w-4" />
            <span>{transactions.length} transactions au total</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50">
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
              {currentTransactions.map((transaction) => (
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
                    {formatAmount(transaction.amount, transaction.currency)}
                  </TableCell>
                  <TableCell>
                    <span className="capitalize text-sm">
                      {transaction.transaction_type}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm text-gray-600">
                    {formatDate(transaction.timestamp)}
                  </TableCell>
                  <TableCell>
                    <FraudScoreCell score={transaction.fraud_score} />
                  </TableCell>
                  <TableCell>
                    <StatusBadge 
                      isFraud={transaction.is_fraud} 
                      fraudScore={transaction.fraud_score} 
                    />
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewDetails?.(transaction)}
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
              Page {currentPage} sur {totalPages} ({transactions.length} transactions)
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};