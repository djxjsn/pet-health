
'use client';

import type { NextPage } from 'next';
import { useState, useRef, useEffect } from 'react';
import { chatApi } from '@/api/chat';
import AuthModal from '@/components/auth/AuthModal';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const ChatPage: NextPage = () => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '我是您的 AI 宠物健康助手，请问有什么可以帮您？' },
  ]);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const data = await chatApi.sendMessage({ message: inputValue });
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || '抱歉，我无法回答这个问题。',
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      const error = err as { status?: number; message?: string };
      if (error.status === 401) {
        setShowAuthModal(true);
        return;
      }
      let errorMsg = '抱歉，发生了错误，请稍后重试。';
      if (error.status === 504) {
        errorMsg = '请求处理超时，AI 正在思考中，请稍后重试或简化您的问题。';
      } else if (error.message?.includes('超时')) {
        errorMsg = '网络请求超时，请检查网络连接后重试。';
      } else if (error.status === 500) {
        errorMsg = '服务器内部错误，请稍后重试。';
      } else if (error.message) {
        errorMsg = error.message;
      }
      setMessages((prev) => [...prev, { role: 'assistant', content: errorMsg }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  return (
    <div className="flex h-screen flex-col bg-neutral-50">
      <header className="flex h-16 flex-shrink-0 items-center justify-between border-b bg-white px-4 md:h-14">
        <div className="flex items-center space-x-4">
          <button className="md:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-neutral-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" /></svg>
          </button>
          <h1 className="text-lg font-semibold md:text-xl text-neutral-900">AI 宠物健康助手</h1>
        </div>
        <div className="flex items-center space-x-4">
          <div className="h-8 w-8 rounded-full bg-primary-500"></div>
        </div>
      </header>

      <main className="flex flex-1 overflow-hidden">
        <div className="flex flex-1 flex-col">
          <div className="flex-1 overflow-y-auto p-4 md:p-6">
            <div className="space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex items-start space-x-3 ${
                    msg.role === 'user' ? 'justify-end' : ''
                  }`}
                >
                  {msg.role === 'assistant' && (
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-primary-500 text-white">
                      🤖
                    </div>
                  )}
                  <div
                    className={`max-w-lg rounded-lg ${
                      msg.role === 'user'
                        ? 'rounded-br-none bg-primary-500 text-white'
                        : 'rounded-tl-none bg-white text-neutral-800 border border-neutral-100'
                    } p-3 shadow-sm`}
                  >
                    <p className="text-sm">{msg.content}</p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-accent-500 text-white">
                      👤
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex items-start space-x-3">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-primary-500 text-white">
                    🤖
                  </div>
                  <div className="max-w-lg rounded-lg rounded-tl-none bg-white text-neutral-800 border border-neutral-100 p-3 shadow-sm">
                    <div className="flex items-center space-x-2">
                      <div className="h-2 w-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="h-2 w-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="h-2 w-2 rounded-full bg-primary-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="border-t bg-white p-4 md:p-6">
            <div className="relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入您的问题..."
                className="w-full rounded-full border border-neutral-300 py-3 pl-5 pr-12 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                onClick={handleSendMessage}
                className="absolute inset-y-0 right-0 flex items-center pr-4"
              >
                <svg className="h-6 w-6 text-primary-500 hover:text-primary-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 16.571V11.5a1 1 0 011-1h.001a1 1 0 011 1v5.071a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" /></svg>
              </button>
            </div>
          </div>
        </div>

        <aside className="hidden w-80 flex-shrink-0 overflow-y-auto border-l bg-white p-4 lg:block">
          <h2 className="mb-4 text-lg font-semibold text-neutral-800">当前宠物信息</h2>
          <div className="rounded-lg bg-neutral-50 p-4 border border-neutral-100">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">🐕</div>
              <div>
                <div className="font-semibold text-neutral-900">豆豆</div>
                <div className="text-sm text-neutral-500">金毛 · 2岁</div>
              </div>
            </div>
          </div>
        </aside>
      </main>
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </div>
  );
};

export default ChatPage;