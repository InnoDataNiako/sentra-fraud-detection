/**
 * App - Point d'entrée de l'application avec routing
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { Dashboard, Detection, History } from '@/pages';
import { Analytics } from '@/pages/Analytics';
import { useEffect, useState } from 'react';
import { fixLeafletIcons } from './components/RiskMap';
import { testConnection } from './services/api';
import { Toaster } from 'react-hot-toast';

function App() {
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);

  useEffect(() => {
    fixLeafletIcons();
    
    // Tester la connexion API au démarrage
    const checkApiConnection = async () => {
      try {
        const connected = await testConnection();
        setApiConnected(connected);
        
        if (!connected) {
          console.warn('⚠️ API non connectée. Vérifiez que le backend est lancé.');
        } else {
          console.log('✅ API connectée avec succès');
        }
      } catch (error) {
        setApiConnected(false);
        console.error('❌ Erreur lors du test de connexion API:', error);
      }
    };
    
    checkApiConnection();
  }, []);

  // Afficher un loader pendant la vérification
  if (apiConnected === null) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Vérification de la connexion...</p>
        </div>
      </div>
    );
  }

  // Afficher un avertissement si API non connectée
  if (apiConnected === false && import.meta.env.DEV) {
    console.warn('🚨 Le backend n\'est pas connecté. Lancez-le avec: docker-compose up');
  }

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="/detection" element={<Detection />} />
            <Route path="history" element={<History />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="settings" element={<div className="p-8">Paramètres (bientôt)</div>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </>
  );
}

export default App;