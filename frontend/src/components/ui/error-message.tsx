/**
 * Composant Error Message - Affichage d'erreurs
 */

import { AlertCircle, XCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from './alert';
import { Button } from './button';
import { cn } from '@/lib/utils';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
  variant?: 'destructive' | 'warning';
}

export function ErrorMessage({
  title = 'Une erreur est survenue',
  message,
  onRetry,
  className,
  variant = 'destructive',
}: ErrorMessageProps) {
  return (
    <Alert variant={variant} className={cn('animate-fade-in', className)}>
      <XCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription className="flex items-center justify-between gap-4">
        <span>{message}</span>
        {onRetry && (
          <Button onClick={onRetry} variant="outline" size="sm">
            Réessayer
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}

/**
 * Composant d'erreur inline
 */
interface InlineErrorProps {
  message: string;
  className?: string;
}

export function InlineError({ message, className }: InlineErrorProps) {
  return (
    <div className={cn('flex items-center gap-2 text-sm text-red-600', className)}>
      <AlertCircle className="h-4 w-4" />
      <span>{message}</span>
    </div>
  );
}