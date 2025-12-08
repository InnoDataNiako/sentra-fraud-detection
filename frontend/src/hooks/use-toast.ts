// frontend/src/hooks/use-toast.ts
import { useState } from 'react';

export interface ToastOptions {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

export interface Toast extends ToastOptions {
  id: string;
  open: boolean;
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = (options: ToastOptions) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: Toast = {
      id,
      open: true,
      ...options,
    };
    
    setToasts(prev => [...prev, newToast]);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
    
    // Also log to console for debugging
    console.log(`[Toast] ${options.title}: ${options.description || ''}`);
  };

  const dismiss = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return {
    toasts,
    toast,
    dismiss,
  };
}