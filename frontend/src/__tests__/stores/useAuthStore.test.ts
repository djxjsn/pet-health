import '@testing-library/jest-dom';
import { act } from '@testing-library/react';
import { useAuthStore } from '@/stores/useAuthStore';
import type { User } from '@/types';

const mockUser: User = {
  user_id: 'user-001',
  phone: '13800138000',
  email: 'test@example.com',
  nickname: '测试用户',
  avatar_url: 'https://example.com/avatar.png',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  describe('初始状态', () => {
    it('应该有正确的默认值', () => {
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });
  });

  describe('login', () => {
    it('登录后应设置用户和认证状态', () => {
      const { login } = useAuthStore.getState();

      act(() => {
        login(mockUser, 'test-token-123');
      });

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.token).toBe('test-token-123');
      expect(state.isAuthenticated).toBe(true);
      expect(state.isLoading).toBe(false);
    });

    it('登录后 isLoading 应为 false', () => {
      const { login, setLoading } = useAuthStore.getState();

      act(() => {
        setLoading(true);
        login(mockUser, 'token');
      });

      expect(useAuthStore.getState().isLoading).toBe(false);
    });
  });

  describe('logout', () => {
    it('登出后应清除所有状态', () => {
      const { login, logout } = useAuthStore.getState();

      act(() => {
        login(mockUser, 'token');
      });

      act(() => {
        logout();
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });
  });

  describe('updateProfile', () => {
    it('应该更新用户信息', () => {
      const { login, updateProfile } = useAuthStore.getState();

      act(() => {
        login(mockUser, 'token');
      });

      act(() => {
        updateProfile({ nickname: '新昵称' });
      });

      expect(useAuthStore.getState().user?.nickname).toBe('新昵称');
    });

    it('无用户时不应报错', () => {
      const { updateProfile } = useAuthStore.getState();

      expect(() => {
        act(() => {
          updateProfile({ nickname: '新昵称' });
        });
      }).not.toThrow();
    });
  });

  describe('setUser / setToken', () => {
    it('setUser 应更新用户并设置认证状态', () => {
      const { setUser } = useAuthStore.getState();

      act(() => {
        setUser(mockUser);
      });

      expect(useAuthStore.getState().user).toEqual(mockUser);
      expect(useAuthStore.getState().isAuthenticated).toBe(true);
    });

    it('setUser(null) 应清除认证状态', () => {
      const { setUser, login } = useAuthStore.getState();

      act(() => {
        login(mockUser, 'token');
        setUser(null);
      });

      expect(useAuthStore.getState().user).toBeNull();
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });
  });
});
