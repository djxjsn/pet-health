'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { Conversation, Message } from '@/types';
import { formatRelativeTime } from '@/utils';

export default function HistoryPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data for development
  const mockConversations: Conversation[] = [
    {
      conversation_id: 'conv-001',
      user_id: 'user-001',
      pet_id: 'pet-001',
      title: '关于猫咪呕吐的咨询',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      updated_at: new Date().toISOString(),
      messages: [
        {
          message_id: 'msg-001',
          conversation_id: 'conv-001',
          role: 'user',
          content: '我的猫今天早上吐了两次，精神不太好，需要看医生吗？',
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
          message_id: 'msg-002',
          conversation_id: 'conv-001',
          role: 'assistant',
          content: '根据您的描述，猫咪呕吐可能由以下原因引起：\n\n**常见原因：**\n1. 毛球问题（最常见）\n2. 进食过快\n3. 食物不耐受\n4. 胃炎或肠胃不适\n\n**建议观察指标：**\n- 精神状态是否正常\n- 是否有食欲\n- 大便情况如何\n- 呕吐物是否有血丝\n\n⚠️ 如果出现以下情况，请立即就医：\n- 连续呕吐超过24小时\n- 呕吐物带血\n- 精神萎靡、不吃不喝\n- 腹部触痛明显',
          created_at: new Date().toISOString(),
        },
      ],
    },
    {
      conversation_id: 'conv-002',
      user_id: 'user-001',
      pet_id: 'pet-002',
      title: '狗狗皮肤瘙痒怎么办',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      updated_at: new Date(Date.now() - 86400000).toISOString(),
      messages: [
        {
          message_id: 'msg-003',
          conversation_id: 'conv-002',
          role: 'user',
          content: '金毛最近总是挠痒，皮肤有些红肿',
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          message_id: 'msg-004',
          conversation_id: 'conv-002',
          role: 'assistant',
          content: '金毛犬皮肤瘙痒的常见原因包括：\n\n**主要病因：**\n1. **寄生虫感染**（跳蚤、螨虫）\n2. **过敏反应**（食物过敏、环境过敏）\n3. **真菌/细菌感染**\n4. **干燥性皮炎**\n\n**初步处理建议：**\n1. 定期体外驱虫（每月一次）\n2. 使用温和的宠物专用沐浴露\n3. 保持环境清洁，定期消毒\n4. 观察饮食是否有变化\n\n📌 **推荐产品**：抗敏洗护套装、宠物益生菌',
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
      ],
    },
    {
      conversation_id: 'conv-003',
      user_id: 'user-001',
      pet_id: 'pet-001',
      title: '幼猫疫苗接种时间表',
      created_at: new Date(Date.now() - 172800000).toISOString(),
      updated_at: new Date(Date.now() - 172800000).toISOString(),
      messages: [],
    },
  ];

  // Load conversations
  const loadConversations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // In production, replace with actual API call:
      // const response = await fetch('/api/v1/conversations');
      // const data = await response.json();
      
      setConversations(mockConversations);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('加载历史记录失败');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Filter conversations by search query
  const filteredConversations = conversations.filter(conv =>
    conv.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.messages?.some(msg => msg.content.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Handle conversation selection
  const handleSelectConversation = useCallback((conversation: Conversation) => {
    setSelectedConversation(conversation);
  }, []);

  // Handle delete conversation
  const handleDeleteConversation = useCallback(async (conversationId: string) => {
    if (!confirm('确定要删除这条对话吗？')) return;

    try {
      // Simulate API call
      setConversations(prev => prev.filter(c => c.conversation_id !== conversationId));
      if (selectedConversation?.conversation_id === conversationId) {
        setSelectedConversation(null);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  }, [selectedConversation]);

  // Handle feedback
  const handleFeedback = useCallback((messageId: string, feedback: 'helpful' | 'not_helpful') => {
    console.log(`Feedback ${feedback} for message ${messageId}`);
    // Send to API in production
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b bg-white px-4 py-3 md:hidden">
        <h1 className="text-lg font-semibold text-gray-900">历史对话</h1>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-6">
        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索对话内容..."
              className="w-full rounded-lg border border-gray-200 bg-white py-2.5 pl-10 pr-4 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-200"
            />
          </div>
        </div>

        {/* Content Area */}
        <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
          {/* Conversation List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-gray-500">
                共 {filteredConversations.length} 条对话
              </h2>
              <button
                onClick={loadConversations}
                disabled={isLoading}
                className="text-sm text-primary-600 hover:text-primary-700 disabled:text-gray-300"
              >
                {isLoading ? '加载中...' : '刷新'}
              </button>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="flex flex-col items-center justify-center rounded-lg bg-white p-12 text-center">
                <div className="mb-4 h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-primary-600" />
                <p className="text-sm text-gray-500">加载中...</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-center">
                <p className="text-sm text-red-600">{error}</p>
                <button
                  onClick={loadConversations}
                  className="mt-2 text-sm font-medium text-red-700 underline hover:text-red-800"
                >
                  重试
                </button>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && !error && filteredConversations.length === 0 && (
              <div className="flex flex-col items-center justify-center rounded-lg bg-white p-12 text-center">
                <svg className="mb-4 h-16 w-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p className="text-sm font-medium text-gray-900">暂无历史对话</p>
                <p className="mt-1 text-sm text-gray-500">
                  {searchQuery ? '没有找到匹配的对话' : '开始一段新的对话吧'}
                </p>
                {!searchQuery && (
                  <Link
                    href="/chat"
                    className="mt-4 inline-flex items-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
                  >
                    开始新对话 →
                  </Link>
                )}
              </div>
            )}

            {/* Conversation List Items */}
            {!isLoading && filteredConversations.map(conversation => (
              <div
                key={conversation.conversation_id}
                onClick={() => handleSelectConversation(conversation)}
                className={`group cursor-pointer rounded-lg border bg-white p-4 transition-all ${
                  selectedConversation?.conversation_id === conversation.conversation_id
                    ? 'border-primary-500 ring-1 ring-primary-200'
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="truncate font-medium text-gray-900">
                      {conversation.title || '未命名对话'}
                    </h3>
                    
                    {/* Preview of last message */}
                    {conversation.messages && conversation.messages.length > 0 && (
                      <p className="mt-1 truncate text-sm text-gray-500">
                        {conversation.messages[conversation.messages.length - 1].content.slice(0, 100)}...
                      </p>
                    )}

                    <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
                      <span>{formatRelativeTime(conversation.updated_at)}</span>
                      <span>·</span>
                      <span>{conversation.messages?.length || 0} 条消息</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="ml-4 flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteConversation(conversation.conversation_id);
                      }}
                      className="rounded p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-500"
                      title="删除"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Conversation Detail Panel (Desktop) */}
          {selectedConversation && (
            <div className="hidden lg:block rounded-lg border border-gray-200 bg-white">
              <div className="border-b border-gray-100 px-4 py-3">
                <h2 className="font-semibold text-gray-900 truncate">
                  {selectedConversation.title || '对话详情'}
                </h2>
              </div>

              <div className="max-h-[calc(100vh-200px)] overflow-y-auto p-4 space-y-4">
                {selectedConversation.messages?.map(message => (
                  <MessageBubble
                    key={message.message_id}
                    message={message}
                    onFeedback={handleFeedback}
                  />
                ))}

                {(!selectedConversation.messages || selectedConversation.messages.length === 0) && (
                  <div className="py-12 text-center text-sm text-gray-500">
                    对话内容为空
                  </div>
                )}
              </div>

              {/* Continue Chat Button */}
              <div className="border-t border-gray-100 p-4">
                <Link
                  href={`/chat?conversation=${selectedConversation.conversation_id}`}
                  className="block w-full rounded-lg bg-primary-600 py-2.5 text-center text-sm font-medium text-white hover:bg-primary-700 transition-colors"
                >
                  继续对话 →
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom padding for mobile nav */}
      <div className="h-20 md:h-0" />
    </div>
  );
}
