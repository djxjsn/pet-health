'use client';

import { apiClient } from './client';
import type { Conversation, Message } from '@/types';
import type { ChatRequest, ChatResponse } from '@/types/api';

export interface ConversationDetail extends Conversation {
  messages?: Array<Message & { metadata?: Record<string, unknown> }>;
  message_count?: number;
}

export interface CreateConversationResponse {
  conversation_id: string;
  user_id: string;
  pet_id?: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export const chatApi = {
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    return apiClient.post<ChatResponse>('/chat', data, { timeout: 180000, retries: 0 });
  },

  async listConversations(skip = 0, limit = 20): Promise<Conversation[]> {
    return apiClient.get<Conversation[]>('/conversations', { skip, limit });
  },

  async getConversation(conversationId: string): Promise<ConversationDetail> {
    return apiClient.get<ConversationDetail>(`/conversations/${conversationId}`);
  },

  async getMessages(conversationId: string, skip = 0, limit = 50): Promise<Message[]> {
    return apiClient.get<Message[]>(`/conversations/${conversationId}/messages`, { skip, limit });
  },

  async createConversation(petId?: string): Promise<CreateConversationResponse> {
    return apiClient.post<CreateConversationResponse>('/conversations', petId ? { pet_id: petId } : undefined);
  },

  async deleteConversation(conversationId: string): Promise<void> {
    return apiClient.delete(`/conversations/${conversationId}`);
  },
};