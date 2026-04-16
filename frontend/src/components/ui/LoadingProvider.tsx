'use client';

import { createContext, useContext, useState, useCallback, ReactNode, memo } from 'react';

interface LoadingState {
  isLoading: boolean;
  message?: string;
}

interface LoadingContextType extends LoadingState {
  startLoading: (message?: string) => void;
  stopLoading: () => void;
  withLoading: <T>(fn: () => Promise<T>, message?: string) => Promise<T>;
}

const LoadingContext = createContext<LoadingContextType | null>(null);

export function useLoading() {
  const ctx = useContext(LoadingContext);
  if (!ctx) throw new Error('useLoading must be used within LoadingProvider');
  return ctx;
}

interface LoadingProviderProps {
  children: ReactNode;
}

export function LoadingProvider({ children }: LoadingProviderProps) {
  const [state, setState] = useState<LoadingState>({ isLoading: false });

  const startLoading = useCallback((message?: string) => {
    setState({ isLoading: true, message });
  }, []);

  const stopLoading = useCallback(() => {
    setState({ isLoading: false });
  }, []);

  const withLoading = useCallback(
    async <T,>(fn: () => Promise<T>, message?: string): Promise<T> => {
      startLoading(message);
      try {
        return await fn();
      } finally {
        stopLoading();
      }
    },
    [startLoading, stopLoading]
  );

  return (
    <LoadingContext.Provider value={{ ...state, startLoading, stopLoading, withLoading }}>
      {children}
      {state.isLoading && <GlobalLoadingOverlay message={state.message} />}
    </LoadingContext.Provider>
  );
}

function GlobalLoadingOverlay({ message }: { message?: string }) {
  return (
    <div className="fixed inset-0 z-[9998] flex items-center justify-center bg-black/20 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4 rounded-2xl bg-white px-8 py-6 shadow-xl">
        <Spinner size="lg" />
        {message && (
          <p className="text-sm font-medium text-gray-600">{message}</p>
        )}
      </div>
    </div>
  );
}

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const SIZE_MAP = {
  sm: 'h-4 w-4 border-2',
  md: 'h-6 w-6 border-2',
  lg: 'h-10 w-10 border-[3px]',
};

export const Spinner = memo(function SpinnerComponent({ size = 'md', className = '' }: SpinnerProps) {
  return (
    <div
      className={`animate-spin rounded-full border-primary-200 border-t-primary-600 ${SIZE_MAP[size]} ${className}`}
      role="status"
      aria-label="加载中"
    />
  );
});
