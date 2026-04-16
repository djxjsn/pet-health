'use client';

import type {
  ApiError,
  ApiResponse,
  PaginatedResponse,
  TokenData,
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClientError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

class NetworkError extends Error {
  constructor(message: string, public originalError?: Error) {
    super(message);
    this.name = 'NetworkError';
  }
}

interface RequestConfig extends Omit<RequestInit, 'body' | 'headers'> {
  params?: Record<string, string | number | boolean>;
  skipAuth?: boolean;
  retries?: number;
  timeout?: number;
  body?: unknown;
  headers?: Record<string, string>;
}

const DEFAULT_TIMEOUT = 15000;
const MAX_RETRIES = 2;

function buildUrl(endpoint: string, params?: Record<string, string | number | boolean>): string {
  const url = `${API_BASE_URL}${endpoint}`;
  if (!params || Object.keys(params).length === 0) return url;
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    searchParams.set(key, String(value));
  }
  return `${url}?${searchParams.toString()}`;
}

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsed = JSON.parse(authStorage);
      return parsed?.state?.token ?? null;
    }
  } catch { /* ignore */ }
  return null;
}

async function fetchWithTimeout(url: string, options: RequestInit, timeout: number): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timer);
    return response;
  } catch (error) {
    clearTimeout(timer);
    if ((error as Error).name === 'AbortError') {
      throw new NetworkError(`请求超时 (${timeout}ms): ${url}`);
    }
    throw new NetworkError(`网络连接失败: ${(error as Error).message}`, error as Error);
  }
}

function parseErrorResponse(status: number, body: unknown): ApiClientError {
  let detail = '请求失败';
  let code: string | undefined;

  if (body && typeof body === 'object' && 'detail' in body) {
    detail = (body as { detail: string }).detail;
  }

  if (status === 401) detail = '登录已过期，请重新登录';
  else if (status === 403) detail = '没有权限执行此操作';
  else if (status === 404) detail = '请求的资源不存在';
  else if (status >= 500) detail = '服务器内部错误，请稍后重试';

  return new ApiClientError(detail, status, code);
}

export class ApiClient {
  private baseUrl: string;
  private defaultTimeout: number;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || API_BASE_URL;
    this.defaultTimeout = DEFAULT_TIMEOUT;
  }

  async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const {
      params,
      skipAuth = false,
      retries = MAX_RETRIES,
      timeout = this.defaultTimeout,
      method = 'GET',
      body,
      headers: customHeaders,
      ...rest
    } = config;

    const url = buildUrl(endpoint, params);

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(customHeaders as Record<string, string>),
    };

    if (!skipAuth) {
      const token = getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetchWithTimeout(
          url,
          { method, headers, body: body ? JSON.stringify(body) : undefined },
          timeout
        );

        if (!response.ok) {
          let errorBody: unknown;
          try {
            errorBody = await response.json().catch(() => null);
          } catch { /* ignore */ }

          const error = parseErrorResponse(response.status, errorBody);

          // Don't retry on client errors (4xx)
          if (response.status < 500) throw error;

          lastError = error;
          await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
          continue;
        }

        // Handle 204 No Content
        if (response.status === 204) return undefined as T;

        // Handle empty responses
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          return undefined as T;
        }

        const data = await response.json();
        return data as T;
      } catch (error) {
        if (error instanceof ApiClientError) throw error;

        lastError = error instanceof Error ? error : new Error(String(error));

        if (attempt < retries) {
          await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
          continue;
        }

        break;
      }
    }

    throw lastError || new NetworkError('请求失败，请检查网络连接');
  }

  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params, ...config });
  }

  async post<T>(endpoint: string, body?: unknown, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body, ...config });
  }

  async put<T>(endpoint: string, body?: unknown, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body, ...config });
  }

  async delete(endpoint: string, config?: Partial<RequestConfig>): Promise<void> {
    await this.request(endpoint, { method: 'DELETE', ...config });
  }

  setBaseUrl(url: string) {
    this.baseUrl = url;
  }
}

export const apiClient = new ApiClient();

export { ApiClientError, NetworkError };
