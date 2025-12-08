import React, { useState, useEffect } from 'react';
import { RefreshCw, Zap, AlertTriangle } from 'lucide-react';

// === CONFIGURATION DE L'API ===
// IMPORTANT : Assurez-vous que cette URL est correcte !
const API_BASE_URL = "http://localhost:8000/api/v1"; 

// --- Fonction de requête avec gestion des erreurs ---
const checkApiStatus = async (setApiStatus, setMessage) => {
  const healthEndpoint = `${API_BASE_URL}/health`;
  setApiStatus('loading');
  setMessage('Vérification du statut de l\'API...');

  try {
    // Utilisation de Fetch pour la simplicité
    const response = await fetch(healthEndpoint, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });

    if (response.ok) {
      const data = await response.json();
      if (data.status === "OK") {
        setApiStatus('success');
        setMessage(`API connectée avec succès ! Statut : ${data.status} | Version : ${data.version}`);
      } else {
        setApiStatus('error');
        setMessage(`Erreur de santé API (Code 200 mais statut non OK) : ${JSON.stringify(data)}`);
      }
    } else {
      // Gère les erreurs HTTP (4xx, 5xx)
      setApiStatus('error');
      setMessage(`Erreur HTTP : Code ${response.status}. L'API est peut-être inaccessible ou mal configurée.`);
    }

  } catch (error) {
    // Gère les erreurs réseau (CORS, DNS, serveur éteint)
    console.error("Erreur de connexion réseau/CORS:", error);
    setApiStatus('error');
    setMessage(`Échec de la connexion à l'API (${API_BASE_URL}). 
      Vérifiez que le serveur est démarré et que l'URL est correcte. 
      (Erreur: ${error.message})`);
  }
};

const App = () => {
  const [apiStatus, setApiStatus] = useState('idle'); // idle | loading | success | error
  const [message, setMessage] = useState('Cliquez pour vérifier la connexion à l\'API SÉNTRA.');

  useEffect(() => {
    // Si vous voulez vérifier au démarrage :
    // checkApiStatus(setApiStatus, setMessage);
  }, []);

  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'loading':
        return <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />;
      case 'success':
        return <Zap className="w-6 h-6 text-green-500 fill-green-500" />;
      case 'error':
        return <AlertTriangle className="w-6 h-6 text-red-500 fill-red-500" />;
      default:
        return <Zap className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (apiStatus) {
      case 'success': return 'bg-green-100 border-green-400 text-green-800';
      case 'error': return 'bg-red-100 border-red-400 text-red-800';
      case 'loading': return 'bg-blue-100 border-blue-400 text-blue-800';
      default: return 'bg-gray-100 border-gray-300 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white p-8 rounded-xl shadow-2xl space-y-6">
        <h1 className="text-3xl font-extrabold text-gray-900 text-center">
          SÉNTRA - API Health Checker
        </h1>
        <p className="text-gray-500 text-center">
          URL de base configurée : <code className="font-mono text-sm bg-gray-200 p-1 rounded">{API_BASE_URL}</code>
        </p>

        <div className={`p-4 border-l-4 rounded-lg ${getStatusColor()}`}>
          <div className="flex items-center space-x-3">
            {getStatusIcon()}
            <p className="font-medium text-sm whitespace-pre-wrap">
              {message}
            </p>
          </div>
        </div>

        <button
          onClick={() => checkApiStatus(setApiStatus, setMessage)}
          disabled={apiStatus === 'loading'}
          className="w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition duration-150 ease-in-out"
        >
          {apiStatus === 'loading' ? (
            <>
              <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
              Connexion en cours...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5 mr-2" />
              Vérifier la connexion API (Port 8000)
            </>
          )}
        </button>

        <p className="text-xs text-gray-400 text-center pt-4">
          Si l'erreur persiste, assurez-vous que `API_BASE_URL` est correct et que votre serveur FastAPI est bien démarré sur le port 8000.
        </p>
      </div>
    </div>
  );
};

export default App;