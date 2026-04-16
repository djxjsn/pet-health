'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/useAuthStore';

interface UseAuthOptions {
  redirectTo?: string;
  redirectIfAuth?: string;
}

export function useAuth(options: UseAuthOptions = {}) {
  const { redirectTo = '/login', redirectIfAuth } = options;
  const router = useRouter();
  const pathname = usePathname();
  const { user, token, isAuthenticated, isLoading, login, logout, updateProfile, setLoading } =
    useAuthStore();

  const requireAuth = () => {
    if (!isAuthenticated) {
      router.push(`${redirectTo}?redirect=${encodeURIComponent(pathname)}`);
      return false;
    }
    return true;
  };

  const redirectIfAuthenticated = () => {
    if (isAuthenticated && redirectIfAuth) {
      router.replace(redirectIfAuth);
      return true;
    }
    return false;
  };

  const handleLogout = () => {
    logout();
    document.cookie = 'auth-token=; path=/; max-age=0';
    router.push(redirectTo);
  };

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout: handleLogout,
    updateProfile,
    setLoading,
    requireAuth,
    redirectIfAuthenticated,
  };
}
