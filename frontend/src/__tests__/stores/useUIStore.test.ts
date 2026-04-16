import '@testing-library/jest-dom';
import { act } from '@testing-library/react';
import { useUIStore } from '@/stores/useUIStore';

describe('useUIStore', () => {
  beforeEach(() => {
    useUIStore.setState({
      sidebarCollapsed: false,
      rightPanelVisible: true,
      activeModal: null,
      isMobileMenuOpen: false,
    });
  });

  describe('初始状态', () => {
    it('侧边栏默认展开，右侧面板默认可见', () => {
      const state = useUIStore.getState();
      expect(state.sidebarCollapsed).toBe(false);
      expect(state.rightPanelVisible).toBe(true);
      expect(state.activeModal).toBeNull();
    });
  });

  describe('toggleSidebar', () => {
    it('应切换侧边栏折叠状态', () => {
      const { toggleSidebar } = useUIStore.getState();

      act(() => toggleSidebar());
      expect(useUIStore.getState().sidebarCollapsed).toBe(true);

      act(() => toggleSidebar());
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });
  });

  describe('toggleRightPanel', () => {
    it('应切换右侧面板可见性', () => {
      const { toggleRightPanel } = useUIStore.getState();

      act(() => toggleRightPanel());
      expect(useUIStore.getState().rightPanelVisible).toBe(false);

      act(() => toggleRightPanel());
      expect(useUIStore.getState().rightPanelVisible).toBe(true);
    });
  });

  describe('模态框管理', () => {
    it('openModal 应设置活动模态框 ID', () => {
      const { openModal } = useUIStore.getState();

      act(() => openModal('add-pet'));

      expect(useUIStore.getState().activeModal).toBe('add-pet');
    });

    it('closeModal 应清除活动模态框', () => {
      const { openModal, closeModal } = useUIStore.getState();

      act(() => {
        openModal('edit-profile');
        closeModal();
      });

      expect(useUIStore.getState().activeModal).toBeNull();
    });
  });

  describe('移动端菜单', () => {
    it('setMobileMenuOpen 应设置菜单状态', () => {
      const { setMobileMenuOpen } = useUIStore.getState();

      act(() => setMobileMenuOpen(true));
      expect(useUIStore.getState().isMobileMenuOpen).toBe(true);

      act(() => setMobileMenuOpen(false));
      expect(useUIStore.getState().isMobileMenuOpen).toBe(false);
    });
  });
});
