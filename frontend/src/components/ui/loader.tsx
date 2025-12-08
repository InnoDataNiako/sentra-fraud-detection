/**
 * Composant Loader - Indicateur de chargement
 */

import { cn } from '@/lib/utils';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  text?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
};

export function Loader({ size = 'md', className, text }: LoaderProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <div
        className={cn(
          'animate-spin rounded-full border-primary-500 border-t-transparent',
          sizeClasses[size]
        )}
        role="status"
        aria-label="Chargement"
      />
      {text && (
        <p className="text-sm text-gray-600 animate-pulse">{text}</p>
      )}
    </div>
  );
}

/**
 * Loader pleine page
 */
export function FullPageLoader({ text = 'Chargement...' }: { text?: string }) {
  return (
    <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
      <Loader size="lg" text={text} />
    </div>
  );
}

/**
 * Loader inline pour boutons
 */
export function ButtonLoader() {
  return (
    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
  );
}