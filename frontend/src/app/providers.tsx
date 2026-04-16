'use client';

import { ReactNode } from 'react';
import { ThemeProvider } from '@/components/ThemeProvider';
import { LoadingProvider } from '@/components/ui/LoadingProvider';
import { DynamicToaster } from '@/components/DynamicComponents';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <LoadingProvider>
        {children}
        <DynamicToaster />
      </LoadingProvider>
    </ThemeProvider>
  );
}
