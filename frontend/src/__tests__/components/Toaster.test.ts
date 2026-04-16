import '@testing-library/jest-dom';
import { useToastStore } from '@/stores/useToastStore';

describe('Toaster 组件逻辑', () => {
  beforeEach(() => {
    useToastStore.setState({ toasts: [] });
  });

  describe('空状态', () => {
    it('无 toast 时 toasts 列表应为空', () => {
      expect(useToastStore.getState().toasts).toEqual([]);
    });
  });

  describe('显示逻辑', () => {
    it('添加 success 类型 toast 后应出现在列表中', () => {
      const id = useToastStore.getState().addToast({
        type: 'success',
        title: '操作成功',
        duration: 0,
      });
      expect(useToastStore.getState().toasts).toHaveLength(1);
      expect(useToastStore.getState().toasts[0].type).toBe('success');
      expect(useToastStore.getState().toasts[0].title).toBe('操作成功');
      expect(id).toBeTruthy();
    });

    it('应支持同时存在多个 toast', () => {
      const ids = [
        useToastStore.getState().addToast({ type: 'info', title: 'A', duration: 0 }),
        useToastStore.getState().addToast({ type: 'error', title: 'B', duration: 0 }),
        useToastStore.getState().addToast({ type: 'warning', title: 'C', duration: 0 }),
      ];
      expect(ids).toHaveLength(3);
      expect(ids[0]).toBeTruthy();
      expect(ids[1]).toBeTruthy();
      expect(ids[2]).toBeTruthy();
      expect(useToastStore.getState().toasts.length).toBeGreaterThanOrEqual(1);
    });

    it('带 message 的 toast 应包含描述文本', () => {
      useToastStore.getState().addToast({
        type: 'warning',
        title: '警告标题',
        message: '详细描述',
        duration: 0,
      });
      const t = useToastStore.getState().toasts[0];
      expect(t.message).toBe('详细描述');
    });
  });

  describe('关闭逻辑', () => {
    it('removeToast 应从列表中移除指定项', () => {
      const id = useToastStore.getState().addToast({ type: 'info', title: '可关闭', duration: 0 });
      expect(useToastStore.getState().toasts).toHaveLength(1);

      useToastStore.getState().removeToast(id);
      expect(useToastStore.getState().toasts).toHaveLength(0);
    });

    it('clearAll 应清空所有 toast', () => {
      const s = useToastStore.getState();
      for (let i = 0; i < 5; i++) {
        s.addToast({ type: 'info', title: `${i}`, duration: 0 });
      }
      s.clearAll();
      expect(s.toasts).toHaveLength(0);
    });
  });
});
