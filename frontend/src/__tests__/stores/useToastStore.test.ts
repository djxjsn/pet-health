import '@testing-library/jest-dom';
import { act } from '@testing-library/react';
import { useToastStore, toast } from '@/stores/useToastStore';

describe('useToastStore', () => {
  beforeEach(() => {
    useToastStore.setState({ toasts: [] });
  });

  describe('初始状态', () => {
    it('应该有空的 toast 列表', () => {
      expect(useToastStore.getState().toasts).toEqual([]);
    });
  });

  describe('addToast', () => {
    it('应添加 toast 到列表', () => {
      const id = act(() =>
        useToastStore.getState().addToast({
          type: 'success',
          title: '操作成功',
        })
      );

      const { toasts } = useToastStore.getState();
      expect(toasts).toHaveLength(1);
      expect(toasts[0].type).toBe('success');
      expect(toasts[0].title).toBe('操作成功');
      expect(toasts[0].id).toBeTruthy();
    });

    it('应返回唯一的 toast ID', () => {
      const id1 = useToastStore.getState().addToast({ type: 'info', title: 'A' });
      const id2 = useToastStore.getState().addToast({ type: 'info', title: 'B' });

      expect(id1).not.toBe(id2);
    });

    it('error 类型默认 duration 应为 6000ms', () => {
      useToastStore.getState().addToast({
        type: 'error',
        title: '错误',
      });

      expect(useToastStore.getState().toasts[0].duration).toBe(6000);
    });

    it('其他类型默认 duration 应为 4000ms', () => {
      useToastStore.getState().addToast({
        type: 'success',
        title: '成功',
      });

      expect(useToastStore.getState().toasts[0].duration).toBe(4000);
    });

    it('自定义 duration 应覆盖默认值', () => {
      useToastStore.getState().addToast({
        type: 'success',
        title: '测试',
        duration: 10000,
      });

      expect(useToastStore.getState().toasts[0].duration).toBe(10000);
    });
  });

  describe('removeToast', () => {
    it('应从列表中移除指定 toast', () => {
      const id = useToastStore.getState().addToast({
        type: 'info',
        title: '待移除',
      });

      act(() => {
        useToastStore.getState().removeToast(id);
      });

      expect(useToastStore.getState().toasts).toHaveLength(0);
    });
  });

  describe('clearAll', () => {
    it('应清空所有 toast', () => {
      for (let i = 0; i < 5; i++) {
        useToastStore.getState().addToast({
          type: 'info',
          title: `消息${i}`,
          duration: 0,
        });
      }

      act(() => {
        useToastStore.getState().clearAll();
      });

      expect(useToastStore.getState().toasts).toHaveLength(0);
    });
  });
});

describe('toast 快捷函数', () => {
  beforeEach(() => {
    useToastStore.setState({ toasts: [] });
  });

  it('toast.success 应创建 success 类型的 toast', () => {
    toast.success('保存成功');

    expect(useToastStore.getState().toasts[0]).toMatchObject({
      type: 'success',
      title: '保存成功',
    });
  });

  it('toast.error 应创建 error 类型的 toast', () => {
    toast.error('网络错误', '请检查网络连接');

    const t = useToastStore.getState().toasts[0];
    expect(t.type).toBe('error');
    expect(t.title).toBe('网络错误');
    expect(t.message).toBe('请检查网络连接');
  });

  it('toast.warning 应创建 warning 类型的 toast', () => {
    toast.warning('警告');

    expect(useToastStore.getState().toasts[0].type).toBe('warning');
  });

  it('toast.info 应创建 info 类型的 toast', () => {
    toast.info('提示信息');

    expect(useToastStore.getState().toasts[0].type).toBe('info');
  });
});
