'use client';

import { useEffect, useState, useMemo } from 'react';
import { useToastStore, type Toast, type ToastType } from '@/stores/useToastStore';

const ICON_MAP: Record<ToastType, { path: string; color: string; bg: string }> = {
  success: {
    path: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
  },
  error: {
    path: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'text-red-600',
    bg: 'bg-red-50',
  },
  warning: {
    path: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z',
    color: 'text-amber-600',
    bg: 'bg-amber-50',
  },
  info: {
    path: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'text-blue-600',
    bg: 'bg-blue-50',
  },
};

function ToastItem({ toast: t }: { toast: Toast }) {
  const removeToast = useToastStore((s) => s.removeToast);
  const [isExiting, setIsExiting] = useState(false);
  const icon = useMemo(() => ICON_MAP[t.type], [t.type]);

  useEffect(() => {
    if (t.duration && t.duration > 0) {
      const exitTimer = setTimeout(() => setIsExiting(true), t.duration - 300);
      return () => clearTimeout(exitTimer);
    }
  }, [t.duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => removeToast(t.id), 300);
  };

  return (
    <div
      className={`pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl border border-gray-100 bg-white p-4 shadow-lg ring-1 ring-black/5 transition-all duration-300 ${
        isExiting
          ? 'translate-x-full opacity-0'
          : 'translate-x-0 opacity-100'
      }`}
      role="alert"
    >
      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${icon.bg}`}>
        <svg className={`h-4 w-4 ${icon.color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d={icon.path} />
        </svg>
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900">{t.title}</p>
        {t.message && (
          <p className="mt-1 text-sm text-gray-500">{t.message}</p>
        )}
        {t.action && (
          <button
            onClick={t.action.onClick}
            className="mt-2 text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            {t.action.label}
          </button>
        )}
      </div>

      <button
        onClick={handleClose}
        className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

export default function Toaster() {
  const toasts = useToastStore((s) => s.toasts);

  if (toasts.length === 0) return null;

  return (
    <div className="pointer-events-none fixed right-4 top-4 z-[9999] flex flex-col gap-3">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  );
}
