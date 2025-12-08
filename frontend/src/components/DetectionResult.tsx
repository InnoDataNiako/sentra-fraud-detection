// /**
//  * Affichage du résultat de détection de fraude
//  * Montre le verdict, le score, et les explications
//  */

// import React from 'react';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { Badge } from '@/components/ui/badge';
// import { Alert, AlertDescription } from '@/components/ui/alert';
// import { 
//   CheckCircle, 
//   AlertTriangle, 
//   XCircle, 
//   Shield,
//   TrendingUp,
//   Info
// } from 'lucide-react';
// import { DetectionResult as DetectionResultType } from '@/types/fraud';

// interface DetectionResultProps {
//   result: DetectionResultType;
// }

// export const DetectionResult: React.FC<DetectionResultProps> = ({ result }) => {
//   // Déterminer la couleur et l'icône selon le niveau de risque
//   const getRiskConfig = () => {
//     switch (result.risk_level) {
//       case 'critical':
//         return {
//           color: 'bg-red-100 border-red-300 text-red-800',
//           badgeColor: 'bg-red-600 text-white',
//           icon: <XCircle className="h-12 w-12 text-red-600" />,
//           label: 'CRITIQUE',
//         };
//       case 'high':
//         return {
//           color: 'bg-orange-100 border-orange-300 text-orange-800',
//           badgeColor: 'bg-orange-600 text-white',
//           icon: <AlertTriangle className="h-12 w-12 text-orange-600" />,
//           label: 'ÉLEVÉ',
//         };
//       case 'medium':
//         return {
//           color: 'bg-yellow-100 border-yellow-300 text-yellow-800',
//           badgeColor: 'bg-yellow-600 text-white',
//           icon: <AlertTriangle className="h-12 w-12 text-yellow-600" />,
//           label: 'MOYEN',
//         };
//       case 'low':
//         return {
//           color: 'bg-green-100 border-green-300 text-green-800',
//           badgeColor: 'bg-green-600 text-white',
//           icon: <CheckCircle className="h-12 w-12 text-green-600" />,
//           label: 'FAIBLE',
//         };
//       default:
//         return {
//           color: 'bg-gray-100 border-gray-300 text-gray-800',
//           badgeColor: 'bg-gray-600 text-white',
//           icon: <Shield className="h-12 w-12 text-gray-600" />,
//           label: 'INCONNU',
//         };
//     }
//   };

//   const riskConfig = getRiskConfig();

//   return (
//     <div className="space-y-6">
//       {/* Verdict Principal */}
//       <Card className={`border-2 ${riskConfig.color}`}>
//         <CardContent className="pt-6">
//           <div className="text-center">
//             <div className="flex justify-center mb-4">
//               {riskConfig.icon}
//             </div>
            
//             <h2 className="text-2xl font-bold mb-2">
//               {result.is_fraud ? 'Transaction Suspecte Détectée' : 'Transaction Légitime'}
//             </h2>
            
//             <div className="flex justify-center gap-2 mb-4">
//               <Badge className={riskConfig.badgeColor}>
//                 Risque {riskConfig.label}
//               </Badge>
//               {result.should_block && (
//                 <Badge className="bg-red-600 text-white">
//                   BLOCAGE RECOMMANDÉ
//                 </Badge>
//               )}
//             </div>

//             <div className="grid grid-cols-2 gap-4 mt-6 max-w-md mx-auto">
//               <div className="p-3 bg-white rounded-lg border">
//                 <p className="text-sm text-gray-600">Probabilité de Fraude</p>
//                 <p className="text-2xl font-bold">
//                   {(result.fraud_probability * 100).toFixed(1)}%
//                 </p>
//               </div>
              
//               <div className="p-3 bg-white rounded-lg border">
//                 <p className="text-sm text-gray-600">Score de Confiance</p>
//                 <p className="text-2xl font-bold">
//                   {(result.confidence_score * 100).toFixed(1)}%
//                 </p>
//               </div>
//             </div>
//           </div>
//         </CardContent>
//       </Card>

//       {/* Indicateurs de Fraude */}
//     {result.explanation && result.explanation.fraud_indicators && result.explanation.fraud_indicators.length > 0 && (
//       <Card>
//         <CardHeader>
//           <CardTitle className="flex items-center gap-2">
//             <AlertTriangle className="h-5 w-5 text-orange-600" />
//             Indicateurs de Fraude
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           <div className="space-y-2">
//             {result.explanation.fraud_indicators.map((indicator, index) => (
//               <Alert key={index} className="border-orange-200 bg-orange-50">
//                 <AlertDescription className="text-orange-800">
//                   {indicator}
//                 </AlertDescription>
//               </Alert>
//             ))}
//           </div>
//         </CardContent>
//       </Card>
//     )}




//       {/* Facteurs de Risque */}
//       {result.explanation.top_features && Object.keys(result.explanation.top_features).length > 0 && (
//         <Card>
//           <CardHeader>
//             <CardTitle className="flex items-center gap-2">
//               <TrendingUp className="h-5 w-5 text-blue-600" />
//               Facteurs Principaux
//             </CardTitle>
//           </CardHeader>
//           <CardContent>
//             <div className="space-y-3">
//               {Object.entries(result.explanation.top_features)
//                 .sort(([, a], [, b]) => Math.abs(b as number) - Math.abs(a as number))
//                 .slice(0, 5)
//                 .map(([feature, importance]) => {
//                   const importanceValue = importance as number;
//                   const absImportance = Math.abs(importanceValue);
//                   const percentage = (absImportance * 100).toFixed(1);
                  
//                   return (
//                     <div key={feature} className="space-y-1">
//                       <div className="flex justify-between text-sm">
//                         <span className="font-medium capitalize">
//                           {feature.replace(/_/g, ' ')}
//                         </span>
//                         <span className={importanceValue > 0 ? 'text-red-600' : 'text-green-600'}>
//                           {importanceValue > 0 ? '↑' : '↓'} {percentage}%
//                         </span>
//                       </div>
//                       <div className="w-full bg-gray-200 rounded-full h-2">
//                         <div
//                           className={`h-2 rounded-full ${
//                             importanceValue > 0 ? 'bg-red-500' : 'bg-green-500'
//                           }`}
//                           style={{ width: `${Math.min(absImportance * 100, 100)}%` }}
//                         />
//                       </div>
//                     </div>
//                   );
//                 })}
//             </div>
//           </CardContent>
//         </Card>
//       )}

//       {/* Informations Complémentaires */}
//       <Card>
//         <CardHeader>
//           <CardTitle className="flex items-center gap-2">
//             <Info className="h-5 w-5 text-blue-600" />
//             Informations Complémentaires
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           <div className="space-y-3">
//             <div className="flex justify-between py-2 border-b">
//               <span className="text-gray-600">Niveau de Risque</span>
//               <span className="font-medium">{result.risk_level.toUpperCase()}</span>
//             </div>
            
//             <div className="flex justify-between py-2 border-b">
//               <span className="text-gray-600">Action Recommandée</span>
//               <span className="font-medium">
//                 {result.should_block ? 'Bloquer la transaction' : 'Autoriser la transaction'}
//               </span>
//             </div>
            
//             <div className="flex justify-between py-2 border-b">
//               <span className="text-gray-600">Score de Fraude</span>
//               <span className="font-medium">{(result.fraud_probability * 100).toFixed(2)}%</span>
//             </div>
            
//             <div className="flex justify-between py-2">
//               <span className="text-gray-600">Confiance du Modèle</span>
//               <span className="font-medium">{(result.confidence_score * 100).toFixed(2)}%</span>
//             </div>
//           </div>
//         </CardContent>
//       </Card>

//       {/* Message d'Action */}
//       <Alert className={result.should_block ? 'border-red-300 bg-red-50' : 'border-green-300 bg-green-50'}>
//         <AlertDescription className={result.should_block ? 'text-red-800' : 'text-green-800'}>
//           <p className="font-medium mb-1">
//             {result.should_block ? '⚠️ Action Requise' : '✅ Transaction Approuvée'}
//           </p>
//           <p className="text-sm">
//             {result.should_block
//               ? 'Cette transaction présente un risque élevé de fraude. Il est recommandé de la bloquer et de contacter le client pour vérification.'
//               : 'Cette transaction semble légitime. Vous pouvez l\'approuver en toute sécurité.'}
//           </p>
//         </AlertDescription>
//       </Alert>
//     </div>
//   );
// };


/**
 * Affichage du résultat de détection de fraude
 * Montre le verdict, le score, et les explications
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Shield,
  TrendingUp,
  Info
} from 'lucide-react';
import { DetectionResult as DetectionResultType } from '@/types/fraud';

interface DetectionResultProps {
  result: DetectionResultType;
}

export const DetectionResult: React.FC<DetectionResultProps> = ({ result }) => {
  // 🔧 CORRECTION : Vérifier que l'explication existe
  const hasExplanation = result.explanation !== null && result.explanation !== undefined;
  const fraudIndicators = hasExplanation ? result.explanation.fraud_indicators : [];
  const topFeatures = hasExplanation ? result.explanation.top_features : {};

  // Déterminer la couleur et l'icône selon le niveau de risque
  const getRiskConfig = () => {
    switch (result.risk_level) {
      case 'critical':
        return {
          color: 'bg-red-100 border-red-300 text-red-800',
          badgeColor: 'bg-red-600 text-white',
          icon: <XCircle className="h-12 w-12 text-red-600" />,
          label: 'CRITIQUE',
        };
      case 'high':
        return {
          color: 'bg-orange-100 border-orange-300 text-orange-800',
          badgeColor: 'bg-orange-600 text-white',
          icon: <AlertTriangle className="h-12 w-12 text-orange-600" />,
          label: 'ÉLEVÉ',
        };
      case 'medium':
        return {
          color: 'bg-yellow-100 border-yellow-300 text-yellow-800',
          badgeColor: 'bg-yellow-600 text-white',
          icon: <AlertTriangle className="h-12 w-12 text-yellow-600" />,
          label: 'MOYEN',
        };
      case 'low':
        return {
          color: 'bg-green-100 border-green-300 text-green-800',
          badgeColor: 'bg-green-600 text-white',
          icon: <CheckCircle className="h-12 w-12 text-green-600" />,
          label: 'FAIBLE',
        };
      default:
        return {
          color: 'bg-gray-100 border-gray-300 text-gray-800',
          badgeColor: 'bg-gray-600 text-white',
          icon: <Shield className="h-12 w-12 text-gray-600" />,
          label: 'INCONNU',
        };
    }
  };

  const riskConfig = getRiskConfig();

  return (
    <div className="space-y-6">
      {/* Verdict Principal */}
      <Card className={`border-2 ${riskConfig.color}`}>
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              {riskConfig.icon}
            </div>
            
            <h2 className="text-2xl font-bold mb-2">
              {result.is_fraud ? 'Transaction Suspecte Détectée' : 'Transaction Légitime'}
            </h2>
            
            <div className="flex justify-center gap-2 mb-4">
              <Badge className={riskConfig.badgeColor}>
                Risque {riskConfig.label}
              </Badge>
              {result.should_block && (
                <Badge className="bg-red-600 text-white">
                  BLOCAGE RECOMMANDÉ
                </Badge>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6 max-w-md mx-auto">
              <div className="p-3 bg-white rounded-lg border">
                <p className="text-sm text-gray-600">Probabilité de Fraude</p>
                <p className="text-2xl font-bold">
                  {(result.fraud_probability * 100).toFixed(1)}%
                </p>
              </div>
              
              <div className="p-3 bg-white rounded-lg border">
                <p className="text-sm text-gray-600">Score de Confiance</p>
                <p className="text-2xl font-bold">
                  {(result.confidence_score * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Indicateurs de Fraude - CORRIGÉ */}
      {hasExplanation && fraudIndicators && fraudIndicators.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Indicateurs de Fraude
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {fraudIndicators.map((indicator, index) => (
                <Alert key={index} className="border-orange-200 bg-orange-50">
                  <AlertDescription className="text-orange-800">
                    {indicator}
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Facteurs de Risque - CORRIGÉ */}
      {hasExplanation && topFeatures && Object.keys(topFeatures).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Facteurs Principaux
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(topFeatures)
                .sort(([, a], [, b]) => Math.abs(b as number) - Math.abs(a as number))
                .slice(0, 5)
                .map(([feature, importance]) => {
                  const importanceValue = importance as number;
                  const absImportance = Math.abs(importanceValue);
                  const percentage = (absImportance * 100).toFixed(1);
                  
                  return (
                    <div key={feature} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium capitalize">
                          {feature.replace(/_/g, ' ')}
                        </span>
                        <span className={importanceValue > 0 ? 'text-red-600' : 'text-green-600'}>
                          {importanceValue > 0 ? '↑' : '↓'} {percentage}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            importanceValue > 0 ? 'bg-red-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(absImportance * 100, 100)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Informations Complémentaires */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-600" />
            Informations Complémentaires
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Niveau de Risque</span>
              <span className="font-medium">{result.risk_level.toUpperCase()}</span>
            </div>
            
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Action Recommandée</span>
              <span className="font-medium">
                {result.should_block ? 'Bloquer la transaction' : 'Autoriser la transaction'}
              </span>
            </div>
            
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Score de Fraude</span>
              <span className="font-medium">{(result.fraud_probability * 100).toFixed(2)}%</span>
            </div>
            
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Confiance du Modèle</span>
              <span className="font-medium">{(result.confidence_score * 100).toFixed(2)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Message d'Action */}
      <Alert className={result.should_block ? 'border-red-300 bg-red-50' : 'border-green-300 bg-green-50'}>
        <AlertDescription className={result.should_block ? 'text-red-800' : 'text-green-800'}>
          <p className="font-medium mb-1">
            {result.should_block ? '⚠️ Action Requise' : '✅ Transaction Approuvée'}
          </p>
          <p className="text-sm">
            {result.should_block
              ? 'Cette transaction présente un risque élevé de fraude. Il est recommandé de la bloquer et de contacter le client pour vérification.'
              : 'Cette transaction semble légitime. Vous pouvez l\'approuver en toute sécurité.'}
          </p>
        </AlertDescription>
      </Alert>
    </div>
  );
};