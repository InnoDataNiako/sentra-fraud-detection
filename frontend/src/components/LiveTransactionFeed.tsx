import React from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Clock, MapPin, User } from 'lucide-react';

interface LiveTransaction {
  id: string;
  amount: number;
  customerName: string;
  location: string;
  riskScore: number;
  timestamp: string;
  status: 'approved' | 'blocked' | 'pending';
}

interface LiveTransactionFeedProps {
  transactions: LiveTransaction[];
}

export const LiveTransactionFeed: React.FC<LiveTransactionFeedProps> = ({ transactions }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR').format(amount) + ' F CFA';
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="space-y-3"> {/* ENLEVER max-h-[300px] overflow-y-auto */}
      {transactions.length === 0 ? (
        <div className="text-center py-6 text-gray-500"> {/* Réduire py-8 à py-6 */}
          <Clock className="h-6 w-6 mx-auto mb-2 opacity-50" /> {/* Réduire h-8 w-8 à h-6 w-6 */}
          <p className="text-sm">Aucune transaction en temps réel</p>
        </div>
      ) : (
        transactions.map((tx, index) => (
          <motion.div
            key={tx.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-3 bg-white border rounded-lg hover:shadow-sm transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  tx.riskScore > 70 ? 'bg-red-100' : 
                  tx.riskScore > 30 ? 'bg-yellow-100' : 'bg-green-100'
                }`}>
                  <User className={`h-4 w-4 ${
                    tx.riskScore > 70 ? 'text-red-600' : 
                    tx.riskScore > 30 ? 'text-yellow-600' : 'text-green-600'
                  }`} />
                </div>
                <div>
                  <div className="font-medium text-sm">{tx.customerName}</div> {/* text-sm */}
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {tx.location.split(',')[0]} {/* Afficher seulement la ville */}
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="font-bold text-sm">{formatCurrency(tx.amount)}</div> {/* text-sm */}
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant={
                    tx.riskScore > 70 ? "destructive" : 
                    tx.riskScore > 30 ? "outline" : "secondary"
                  } className="text-xs">
                    {tx.riskScore}%
                  </Badge>
                  <span className="text-xs text-gray-500">
                    {formatTime(tx.timestamp)}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))
      )}
    </div>
  );
};