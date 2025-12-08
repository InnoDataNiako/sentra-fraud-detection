/**
 * Page de Détection de Fraude
 * Permet d'analyser une transaction et voir le résultat
 */

import React, { useState } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { DetectionForm } from '@/components/DetectionForm';
import { DetectionResult } from '@/components/DetectionResult';
import { DetectionResult as DetectionResultType } from '@/types/fraud';

export const Detection: React.FC = () => {
  const [detectionResult, setDetectionResult] = useState<DetectionResultType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);

  const handleDetectionComplete = (result: DetectionResultType) => {
    setDetectionResult(result);
    setShowResult(true);
    setError(null);
  };

  const handleDetectionError = (errorMessage: string) => {
    setError(errorMessage);
    setDetectionResult(null);
    setShowResult(false);
  };

  const handleReset = () => {
    setDetectionResult(null);
    setShowResult(false);
    setError(null);
  };

  return (
    <div className="space-y-6 p-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Détection de Fraude</h1>
          <p className="text-gray-500 mt-1">
            Analysez une transaction en temps réel pour détecter d'éventuelles fraudes
          </p>
        </div>
        
        {showResult && (
          <Button
            onClick={handleReset}
            variant="outline"
            className="gap-2"
          >
            <RotateCcw className="h-4 w-4" />
            Nouvelle Analyse
          </Button>
        )}
      </div>

      {/* Message d'erreur */}
      {error && (
        <Alert className="border-red-300 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <p className="font-medium">Erreur</p>
            <p className="text-sm mt-1">{error}</p>
          </AlertDescription>
        </Alert>
      )}

      {/* Contenu principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Formulaire - Toujours visible */}
        <div className={showResult ? '' : 'lg:col-span-2'}>
          <DetectionForm
            onDetectionComplete={handleDetectionComplete}
            onDetectionError={handleDetectionError}
          />
        </div>

        {/* Résultat - Visible après détection */}
        {showResult && detectionResult && (
          <div className="space-y-6">
            <DetectionResult result={detectionResult} />
          </div>
        )}
      </div>

      {/* Message d'aide initial */}
      {!showResult && !error && (
        <div className="mt-8">
          <Alert className="border-blue-300 bg-blue-50">
            <AlertDescription className="text-blue-800">
              <p className="font-medium mb-2">💡 Comment ça marche ?</p>
              <ol className="list-decimal list-inside space-y-1 text-sm">
                <li>Remplissez les informations de la transaction dans le formulaire</li>
                <li>Cliquez sur "Analyser la Transaction"</li>
                <li>Le système SÉNTRA analyse la transaction en temps réel (≈ 2 secondes)</li>
                <li>Vous recevez un rapport détaillé avec le verdict et les explications</li>
              </ol>
              <p className="text-sm mt-3">
                <strong>Précision du modèle :</strong> 99.8% | <strong>Taux de faux positifs :</strong> 0.26%
              </p>
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
};