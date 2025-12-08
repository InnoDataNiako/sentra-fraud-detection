import { useEffect, useState, useCallback } from 'react';

export const useWebSocket = (url: string) => {
  const [data, setData] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = useCallback(() => {
    try {
      const socket = new WebSocket(url);
      
      socket.onopen = () => {
        console.log('WebSocket connected to:', url);
        setIsConnected(true);
      };
      
      socket.onmessage = (event) => {
        console.log('WebSocket message received:', event.data);
        setData(event.data);
      };
      
      socket.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };
      
      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
      
      setWs(socket);
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setIsConnected(false);
    }
  }, [url]);

  useEffect(() => {
    // En développement, simulons une connexion sans vraiment se connecter
    // car ton backend n'a probablement pas encore WebSocket
    const isDev = import.meta.env.DEV;
    
    if (isDev) {
      // Simulation pour le développement
      setIsConnected(true);
      console.log('WebSocket simulé en mode développement');
    } else {
      // En production, on se connecte vraiment
      connect();
    }
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [connect]);

  const send = useCallback((message: any) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify(message));
    }
  }, [ws, isConnected]);

  return { data, isConnected, send };
};