'use client';

import dynamic from 'next/dynamic';
import type { ReactNode } from 'react';

const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-8">
    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
  </div>
);

const LoadingSkeleton = () => (
  <div className="animate-pulse rounded-lg bg-gray-200 p-4">
    <div className="h-48 w-full rounded bg-gray-300" />
  </div>
);

export const DynamicDesktopLayout = dynamic(
  () => import('@/components/layout/DesktopLayout').then((mod) => mod.default),
  {
    ssr: false,
    loading: () => <div className="flex min-h-screen items-center justify-center"><LoadingSpinner /></div>,
  }
);

export const DynamicKnowledgeSourceCard = dynamic(
  () => import('@/components/chat/KnowledgeSourceCard').then((mod) => mod.default),
  {
    ssr: false,
    loading: () => <LoadingSkeleton />,
  }
);

export const DynamicKnowledgeSourcesList = dynamic(
  () => import('@/components/chat/KnowledgeSourceCard').then((mod) => mod.KnowledgeSourcesList),
  {
    ssr: false,
    loading: () => <LoadingSkeleton />,
  }
);

export const DynamicToaster = dynamic(
  () => import('@/components/ui/Toaster').then((mod) => mod.default),
  {
    ssr: false,
  }
);
