import '@testing-library/jest-dom';
import { act } from '@testing-library/react';
import { useChatStore } from '@/stores/useChatStore';
import type { Message, Conversation } from '@/types';

const mockMessages: Message[] = [
  {
    message_id: 'msg-001',
    conversation_id: 'conv-001',
    role: 'user',
    content: '我的狗最近食欲不振',
    created_at: '2026-04-15T10:00:00Z',
  },
  {
    message_id: 'msg-002',
    conversation_id: 'conv-001',
    role: 'assistant',
    content: '根据您的描述，可能的原因有...',
    created_at: '2026-04-15T10:00:05Z',
  },
];

const mockConversation: Conversation = {
  conversation_id: 'conv-001',
  user_id: 'user-001',
  pet_id: 'pet-001',
  title: '狗狗食欲不振咨询',
  created_at: '2026-04-15T10:00:00Z',
  updated_at: '2026-04-15T10:00:05Z',
  messages: mockMessages,
};

describe('useChatStore', () => {
  beforeEach(() => {
    useChatStore.setState({
      conversations: [],
      currentConversationId: null,
      messages: [],
      isStreaming: false,
      isLoading: false,
    });
  });

  describe('初始状态', () => {
    it('应该有正确的默认值', () => {
      const state = useChatStore.getState();
      expect(state.conversations).toEqual([]);
      expect(state.messages).toEqual([]);
      expect(state.isStreaming).toBe(false);
    });
  });

  describe('addConversation', () => {
    it('应添加会话到列表头部', () => {
      const { addConversation } = useChatStore.getState();

      act(() => {
        addConversation(mockConversation);
      });

      const { conversations } = useChatStore.getState();
      expect(conversations).toHaveLength(1);
      expect(conversations[0]).toEqual(mockConversation);
    });

    it('添加会话后应自动切换当前会话并清空消息', () => {
      const { addConversation } = useChatStore.getState();

      act(() => {
        addConversation(mockConversation);
      });

      const state = useChatStore.getState();
      expect(state.currentConversationId).toBe('conv-001');
      expect(state.messages).toEqual([]);
    });
  });

  describe('removeConversation', () => {
    it('应移除指定会话', () => {
      const { addConversation, removeConversation } = useChatStore.getState();

      act(() => {
        addConversation(mockConversation);
        removeConversation('conv-001');
      });

      expect(useChatStore.getState().conversations).toHaveLength(0);
    });

    it('移除当前会话时应重置 currentConversationId 和 messages', () => {
      const { addConversation, setMessages, removeConversation } = useChatStore.getState();

      act(() => {
        addConversation(mockConversation);
        setMessages(mockMessages);
        removeConversation('conv-001');
      });

      const state = useChatStore.getState();
      expect(state.currentConversationId).toBeNull();
      expect(state.messages).toEqual([]);
    });
  });

  describe('addMessage / setMessages', () => {
    it('addMessage 应追加消息到列表', () => {
      const { addMessage } = useChatStore.getState();

      act(() => {
        addMessage(mockMessages[0]);
        addMessage(mockMessages[1]);
      });

      expect(useChatStore.getState().messages).toHaveLength(2);
    });

    it('setMessages 应替换整个消息列表', () => {
      const { setMessages } = useChatStore.getState();

      act(() => {
        setMessages(mockMessages);
      });

      expect(useChatStore.getState().messages).toEqual(mockMessages);
    });
  });

  describe('updateLastAssistantMessage', () => {
    it('应更新最后一条助手消息的内容', () => {
      const { setMessages, updateLastAssistantMessage } = useChatStore.getState();

      act(() => {
        setMessages(mockMessages);
        updateLastAssistantMessage('更新后的回复内容');
      });

      const msgs = useChatStore.getState().messages;
      const lastAssistant = msgs[msgs.length - 1];
      expect(lastAssistant.content).toBe('更新后的回复内容');
    });

    it('无助手消息时不应有副作用', () => {
      const { setMessages, updateLastAssistantMessage } = useChatStore.getState();

      act(() => {
        setMessages([mockMessages[0]]);
        updateLastAssistantMessage('新内容');
      });

      expect(useChatStore.getState().messages[0].content).toBe('我的狗最近食欲不振');
    });
  });

  describe('流式状态管理', () => {
    it('setStreaming 应正确切换流式状态', () => {
      const { setStreaming } = useChatStore.getState();

      act(() => {
        setStreaming(true);
      });
      expect(useChatStore.getState().isStreaming).toBe(true);

      act(() => {
        setStreaming(false);
      });
      expect(useChatStore.getState().isStreaming).toBe(false);
    });
  });

  describe('clearCurrentChat', () => {
    it('应清除当前会话相关所有状态', () => {
      const { addConversation, setMessages, setStreaming, clearCurrentChat } = useChatStore.getState();

      act(() => {
        addConversation(mockConversation);
        setMessages(mockMessages);
        setStreaming(true);
        clearCurrentChat();
      });

      const state = useChatStore.getState();
      expect(state.currentConversationId).toBeNull();
      expect(state.messages).toEqual([]);
      expect(state.isStreaming).toBe(false);
    });
  });
});
