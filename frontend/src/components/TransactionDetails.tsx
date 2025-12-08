import React from 'react';
import { X, AlertCircle, User, CreditCard, Calendar, MapPin, TrendingUp } from 'lucide-react';
import { Transaction } from '@/types/fraud';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';




interface TransactionDetailsProps {
  transaction: Transaction | null;
  isOpen: boolean;
  onClose: () => void;
}

export const TransactionDetails: React.FC<TransactionDetailsProps> = ({
  transaction,
  isOpen,
  onClose,
}) => {
  if (!transaction || !isOpen) return null;

  // Formater les données
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: transaction.currency || 'XOF',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount);
  };
  // const [activeTab, setActiveTab] = useState<'info' | 'explainability'>('info');

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getRiskColor = (score: number) => {
    if (score > 0.7) return 'text-red-600 bg-red-50';
    if (score > 0.4) return 'text-orange-600 bg-orange-50';
    if (score > 0.2) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getRiskLevel = (score: number) => {
    if (score > 0.8) return 'Très élevé';
    if (score > 0.6) return 'Élevé';
    if (score > 0.4) return 'Moyen';
    if (score > 0.2) return 'Faible';
    return 'Très faible';
  };

  const riskPercentage = (transaction.fraud_score * 100).toFixed(1);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* En-tête */}
        <div className="sticky top-0 bg-white p-6 border-b flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold">Détails de la transaction</h2>
            <p className="text-gray-500 text-sm mt-1">
              {transaction.transaction_id}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Contenu */}
        <div className="p-6 space-y-6">
          {/* En-tête avec statut */}
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                {transaction.is_fraud ? (
                  <Badge variant="destructive" className="gap-1 text-sm">
                    <AlertCircle className="h-4 w-4" />
                    Transaction frauduleuse
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="gap-1 text-sm bg-green-100 text-green-800">
                    Transaction légitime
                  </Badge>
                )}
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full ${getRiskColor(transaction.fraud_score)}`}>
              <span className="font-semibold">{getRiskLevel(transaction.fraud_score)}</span>
            </div>
          </div>

          {/* Montant important */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-center">
              <p className="text-gray-600 text-sm">Montant de la transaction</p>
              <p className="text-3xl font-bold mt-2">{formatAmount(transaction.amount)}</p>
            </div>
          </div>

          {/* Grille d'informations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Section Client */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <User className="h-5 w-5 text-blue-600" />
                Informations client
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">ID Client</p>
                  <p className="font-medium">{transaction.customer_id}</p>
                </div>
                {transaction.location && (
                  <div>
                    <p className="text-sm text-gray-500 flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      Localisation
                    </p>
                    <p className="font-medium">{transaction.location}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Section Transaction */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-purple-600" />
                Détails transaction
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Type</p>
                  <p className="font-medium capitalize">{transaction.transaction_type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Date et heure
                  </p>
                  <p className="font-medium">{formatDate(transaction.timestamp)}</p>
                </div>
                {transaction.metadata && (
                  <div>
                    <p className="text-sm text-gray-500">Métadonnées</p>
                    <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto">
                      {JSON.stringify(transaction.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
            
          </div>

          <Separator />

          {/* Section Risque de fraude */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-orange-600" />
              Analyse du risque
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">Score de risque</span>
                  <span className="font-semibold">{riskPercentage}%</span>
                </div>
                <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      transaction.fraud_score > 0.7 ? 'bg-red-500' :
                      transaction.fraud_score > 0.4 ? 'bg-orange-500' :
                      transaction.fraud_score > 0.2 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${riskPercentage}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Faible risque</span>
                  <span>Risque élevé</span>
                </div>
              </div>

              {transaction.is_fraud && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-red-800">Alerte de fraude confirmée</p>
                      <p className="text-red-700 text-sm mt-1">
                        Cette transaction a été identifiée comme frauduleuse par le système.
                        Actions recommandées : bloquer le compte, contacter le client.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {!transaction.is_fraud && transaction.fraud_score > 0.5 && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-orange-800">Transaction suspecte</p>
                      <p className="text-orange-700 text-sm mt-1">
                        Cette transaction présente des caractéristiques inhabituelles.
                        Surveillance recommandée.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Fermer
            </Button>
            {transaction.is_fraud && (
              <Button variant="destructive">
                <AlertCircle className="h-4 w-4 mr-2" />
                Signaler aux autorités
              </Button>
            )}
            <Button>
              <CreditCard className="h-4 w-4 mr-2" />
              Voir toutes les transactions du client
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};