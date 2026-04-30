'use client';

import { apiClient, ApiClientError } from './client';
import type {
  TokenData,
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
} from '@/types/api';
import type { User } from '@/types';

interface UserResponse extends User {
  is_active?: boolean;
}

export const authApi = {
  async login(data: LoginRequest): Promise<TokenData> {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/login`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let detail = '登录失败';
        try {
          const errorBody = await response.json().catch(() => null);
          if (errorBody?.detail) detail = errorBody.detail;
        } catch { /* ignore */ }
        throw new Error(detail);
      }

      return response.json() as Promise<TokenData>;
    } catch (error) {
      if (error instanceof Error && (error as Error).name !== 'ApiClientError') {
        throw new Error(`网络错误: ${(error as Error).message}`);
      }
      throw error;
    }
  },

  async register(data: RegisterRequest): Promise<UserResponse> {
    return apiClient.post<UserResponse>('/auth/register', data);
  },

  async refreshToken(refreshToken: string): Promise<TokenData> {
    return apiClient.post<TokenData>('/auth/refresh', { refresh_token: refreshToken });
  },

  async forgotPassword(phone: string): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>('/auth/forgot-password', null, {
      params: { phone },
    });
  },

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
  },
};
