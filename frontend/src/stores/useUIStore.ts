'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  sidebarCollapsed: boolean;
  rightPanelVisible: boolean;
  activeModal: string | null;
  isMobileMenuOpen: boolean;

  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleRightPanel: () => void;
  setRightPanelVisible: (visible: boolean) => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  setMobileMenuOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      rightPanelVisible: true,
      activeModal: null,
      isMobileMenuOpen: false,

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (sidebarCollapsed) =>
        set({ sidebarCollapsed }),

      toggleRightPanel: () =>
        set((state) => ({ rightPanelVisible: !state.rightPanelVisible })),

      setRightPanelVisible: (rightPanelVisible) =>
        set({ rightPanelVisible }),

      openModal: (modalId) =>
        set({ activeModal: modalId }),

      closeModal: () =>
        set({ activeModal: null }),

      setMobileMenuOpen: (isMobileMenuOpen) =>
        set({ isMobileMenuOpen }),
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        rightPanelVisible: state.rightPanelVisible,
      }),
    }
  )
);
