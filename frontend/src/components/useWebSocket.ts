import { useEffect, useState, useCallback } from 'react';

export const useWebSocket = (url: string) => {
  const [data, setData] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = useCallback(() => {
    const socket = new WebSocket(url);
    
    socket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };
    
    socket.onmessage = (event) => {
      setData(event.data);
    };
    
    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Reconnect after 5 seconds
      setTimeout(() => connect(), 5000);
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
    
    setWs(socket);
  }, [url]);

  useEffect(() => {
    connect();
    
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