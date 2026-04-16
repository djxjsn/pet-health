'use client';

import { create } from 'zustand';
import type { Conversation, Message } from '@/types';

interface ChatState {
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  isLoading: boolean;

  setConversations: (conversations: Conversation[]) => void;
  addConversation: (conversation: Conversation) => void;
  removeConversation: (conversationId: string) => void;
  setCurrentConversationId: (id: string | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateLastAssistantMessage: (content: string) => void;
  setStreaming: (streaming: boolean) => void;
  setLoading: (loading: boolean) => void;
  clearCurrentChat: () => void;
}

export const useChatStore = create<ChatState>()((set) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isStreaming: false,
  isLoading: false,

  setConversations: (conversations) =>
    set({ conversations }),

  addConversation: (conversation) =>
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      currentConversationId: conversation.conversation_id,
      messages: [],
    })),

  removeConversation: (conversationId) =>
    set((state) => ({
      conversations: state.conversations.filter(
        (c) => c.conversation_id !== conversationId
      ),
      currentConversationId:
        state.currentConversationId === conversationId
          ? null
          : state.currentConversationId,
      messages:
        state.currentConversationId === conversationId
          ? []
          : state.messages,
    })),

  setCurrentConversationId: (currentConversationId) =>
    set({ currentConversationId }),

  setMessages: (messages) =>
    set({ messages }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  updateLastAssistantMessage: (content) =>
    set((state) => {
      const msgs = [...state.messages];
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === 'assistant') {
          msgs[i] = { ...msgs[i], content };
          break;
        }
      }
      return { messages: msgs };
    }),

  setStreaming: (isStreaming) =>
    set({ isStreaming }),

  setLoading: (isLoading) =>
    set({ isLoading }),

  clearCurrentChat: () =>
    set({
      currentConversationId: null,
      messages: [],
      isStreaming: false,
    }),
}));
