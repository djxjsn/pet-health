'use client';

import { Component, ReactNode, ErrorInfo } from 'react';
import { useToastStore } from '@/stores/useToastStore';

export enum ErrorCategory {
  NETWORK = 'NETWORK',
  AUTH = 'AUTH',
  SERVER = 'SERVER',
  VALIDATION = 'VALIDATION',
  NOT_FOUND = 'NOT_FOUND',
  TIMEOUT = 'TIMEOUT',
  PARSE_ERROR = 'PARSE_ERROR',
  UNKNOWN = 'UNKNOWN',
}

export interface AppError {
  message: string;
  category: ErrorCategory;
  statusCode?: number;
  code?: string;
  originalError?: unknown;
  retryable: boolean;
  userMessage: string;
}

function classifyError(error: unknown): AppError {
  if (error instanceof Response) {
    const status = error.status;

    if (status === 401 || status === 403) {
      return {
        message: status === 401 ? '登录已过期' : '没有权限执行此操作',
        category: ErrorCategory.AUTH,
        statusCode: status,
        retryable: false,
        userMessage: status === 401 ? '请重新登录' : '您没有权限执行此操作',
      };
    }

    if (status === 404) {
      return {
        message: '请求的资源不存在',
        category: ErrorCategory.NOT_FOUND,
        statusCode: status,
        retryable: false,
        userMessage: '内容可能已被删除或不存在',
      };
    }

    if (status >= 400 && status < 500) {
      return {
        message: `请求参数有误 (${status})`,
        category: ErrorCategory.VALIDATION,
        statusCode: status,
        retryable: false,
        userMessage: '请检查输入信息后重试',
      };
    }

    if (status >= 500) {
      return {
        message: `服务器内部错误 (${status})`,
        category: ErrorCategory.SERVER,
        statusCode: status,
        retryable: true,
        userMessage: '服务器暂时不可用，稍后将自动重试',
      };
    }
  }

  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      message: error.message || '网络连接失败',
      category: ErrorCategory.NETWORK,
      retryable: true,
      userMessage: '网络连接异常，请检查网络设置',
      originalError: error,
    };
  }

  if (error instanceof DOMException && error.name === 'AbortError') {
    return {
      message: '请求超时',
      category: ErrorCategory.TIMEOUT,
      retryable: true,
      userMessage: '请求响应时间过长，请稍后重试',
      originalError: error,
    };
  }

  if (error instanceof SyntaxError) {
    return {
      message: '数据解析失败',
      category: ErrorCategory.PARSE_ERROR,
      retryable: false,
      userMessage: '数据格式异常，请联系技术支持',
      originalError: error,
    };
  }

  if (error instanceof Error) {
    const name = (error as { name?: string }).name || '';
    if (name === 'NetworkError') {
      return {
        message: error.message,
        category: ErrorCategory.NETWORK,
        retryable: true,
        userMessage: '无法连接到服务器，请检查网络',
        originalError: error,
      };
    }

    if (name === 'ApiClientError') {
      const apiErr = error as { code?: string; status?: number };
      return {
        message: error.message,
        category: (apiErr.status ?? 500) >= 400 ? ErrorCategory.VALIDATION : ErrorCategory.SERVER,
        statusCode: apiErr.status,
        code: apiErr.code,
        retryable: (apiErr.status ?? 0) >= 500,
        userMessage: error.message,
        originalError: error,
      };
    }
  }

  return {
    message: typeof error === 'string' ? error : '未知错误',
    category: ErrorCategory.UNKNOWN,
    retryable: true,
    userMessage: '发生了未知错误，请刷新页面重试',
    originalError: error,
  };
}

const ERROR_TOAST_CONFIG: Record<ErrorCategory, { type: 'error' | 'warning' | 'info'; duration: number }> = {
  [ErrorCategory.NETWORK]: { type: 'warning', duration: 6000 },
  [ErrorCategory.AUTH]: { type: 'error', duration: 8000 },
  [ErrorCategory.SERVER]: { type: 'error', duration: 8000 },
  [ErrorCategory.VALIDATION]: { type: 'warning', duration: 4000 },
  [ErrorCategory.NOT_FOUND]: { type: 'info', duration: 3000 },
  [ErrorCategory.TIMEOUT]: { type: 'warning', duration: 5000 },
  [ErrorCategory.PARSE_ERROR]: { type: 'error', duration: 6000 },
  [ErrorCategory.UNKNOWN]: { type: 'error', duration: 5000 },
};

export function handleAppError(error: unknown, context?: string): AppError {
  const appError = classifyError(error);
  const config = ERROR_TOAST_CONFIG[appError.category];

  console.error(`[Error]${context ? ` ${context}:` : ''}`, appError.message, appError.originalError);

  // Show toast notification
  useToastStore.getState().addToast({
    type: config.type,
    title: appError.userMessage,
    ...(context ? { message: context } : {}),
    duration: config.duration,
    action: appError.retryable ? {
      label: '重试',
      onClick: () => window.location.reload(),
    } : undefined,
  });

  // Handle auth errors - redirect to login
  if (appError.category === ErrorCategory.AUTH && appError.statusCode === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_id');
      document.cookie = 'auth-token=; path=/; max-age=0';
      window.location.href = '/';
    }
  }

  return appError;
}

export async function withErrorHandling<T>(
  fn: () => Promise<T>,
  options?: {
    fallback?: T;
    context?: string;
    showToast?: boolean;
    onError?: (error: AppError) => void;
  }
): Promise<T | undefined> {
  try {
    return await fn();
  } catch (error) {
    const appError = handleAppError(error, options?.context);

    if (options?.onError) {
      options.onError(appError);
    }

    if (options && 'fallback' in options && options.fallback !== undefined) {
      return options.fallback;
    }

    throw appError;
  }
}

// React Error Boundary Component
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    handleAppError(error, 'React Error Boundary');
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-8">
          <div className="max-w-md text-center">
            <div className="mb-4 text-6xl">😵</div>
            <h2 className="mb-2 text-xl font-bold text-gray-900">页面出错了</h2>
            <p className="mb-6 text-sm text-gray-500">
              {this.state.error?.message || '发生了未知错误'}
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => this.setState({ hasError: false, error: null })}
                className="rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                重试
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                返回首页
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
