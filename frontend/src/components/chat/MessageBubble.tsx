'use client';

import { useState, memo } from 'react';
import OptimizedImage from '@/components/OptimizedImage';
import type { Message } from '@/types';

interface KnowledgeSource {
  id: string;
  title: string;
  type: 'knowledge' | 'reference' | 'product';
  url?: string;
  relevance?: number;
}

interface ExtendedMessage extends Message {
  sources?: KnowledgeSource[];
}

interface MessageBubbleProps {
  message: ExtendedMessage;
  isStreaming?: boolean;
  onFeedback?: (messageId: string, feedback: 'helpful' | 'not_helpful') => void;
  onCopy?: (content: string) => void;
  className?: string;
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

function MessageBubble({
  message,
  isStreaming = false,
  onFeedback,
  onCopy,
  className = '',
}: MessageBubbleProps) {
  const [showSources, setShowSources] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const isUser = message.role === 'user';

  const handleCopy = async () => {
    if (onCopy) {
      onCopy(message.content);
    }
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      console.error('Failed to copy');
    }
  };

  const handleFeedback = (type: 'helpful' | 'not_helpful') => {
    setFeedbackGiven(type);
    onFeedback?.(message.message_id, type);
  };

  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''} ${className}`}>
      {/* Avatar */}
      <div
        className={`
          flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-sm font-medium
          ${isUser ? 'bg-blue-500 text-white' : 'bg-primary-500 text-white'}
        `}
      >
        {isUser ? '👤' : '🤖'}
      </div>

      {/* Message Content */}
      <div className={`max-w-[75%] md:max-w-[65%]`}>
        {/* Bubble */}
        <div
          className={`
            relative rounded-2xl px-4 py-2.5 shadow-sm
            ${isUser
              ? 'bg-blue-500 text-white rounded-br-md'
              : 'bg-white text-gray-800 rounded-bl-md border border-gray-100'
            }
          `}
        >
          {/* Content */}
          <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
            {message.content}
            {isStreaming && (
              <span className="inline-block ml-1 h-4 w-0.5 animate-pulse bg-current" />
            )}
          </div>

          {/* Image Attachments */}
          {message.image_urls && message.image_urls.length > 0 && (
            <div className={`mt-2 grid gap-2 ${message.image_urls.length > 1 ? 'grid-cols-2' : 'grid-cols-1'}`}>
              {message.image_urls.map((url, index) => (
                <OptimizedImage
                  key={index}
                  src={url}
                  alt={`附件${index + 1}`}
                  width={400}
                  height={300}
                  className="rounded-lg max-h-48 w-full object-cover"
                />
              ))}
            </div>
          )}

          {/* Sources Section */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-3 border-t border-gray-100 pt-3">
              <button
                onClick={() => setShowSources(!showSources)}
                className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700"
              >
                <svg
                  className={`h-4 w-4 transition-transform ${showSources ? 'rotate-90' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M9 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
                📚 参考来源 ({message.sources.length})
              </button>

              {showSources && (
                <div className="mt-2 space-y-2">
                  {message.sources.map(source => (
                    <div
                      key={source.id}
                      className="flex items-start gap-2 rounded-lg bg-gray-50 p-2.5 text-xs"
                    >
                      <span className="mt-0.5 flex-shrink-0">
                        {source.type === 'knowledge' && '📚'}
                        {source.type === 'reference' && '📄'}
                        {source.type === 'product' && '🛒'}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-800">{source.title}</p>
                        {source.relevance && (
                          <p className="text-gray-500">相关度: {(source.relevance * 100).toFixed(0)}%</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Disclaimer for assistant messages */}
          {!isUser && !isStreaming && (
            <p className="mt-2 text-xs text-gray-400 italic">
              ⚠️ 以上建议仅供参考，如有严重症状请及时就医
            </p>
          )}

          {/* Timestamp */}
          <p
            className={`mt-1.5 text-xs ${
              isUser ? 'text-blue-100' : 'text-gray-400'
            }`}
          >
            {formatTime(message.created_at)}
          </p>
        </div>

        {/* Action Buttons (Assistant only) */}
        {!isUser && !isStreaming && (
          <div className={`mt-2 flex items-center gap-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <button
              onClick={() => handleFeedback('helpful')}
              disabled={feedbackGiven !== null}
              className={`
                rounded-full px-2 py-1 text-xs transition-colors
                ${feedbackGiven === 'helpful'
                  ? 'bg-green-100 text-green-600'
                  : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'
                }
                ${feedbackGiven !== null && feedbackGiven !== 'helpful' ? 'opacity-30' : ''}
              `}
              title="有用"
            >
              👍 有用
            </button>
            <button
              onClick={() => handleFeedback('not_helpful')}
              disabled={feedbackGiven !== null}
              className={`
                rounded-full px-2 py-1 text-xs transition-colors
                ${feedbackGiven === 'not_helpful'
                  ? 'bg-red-100 text-red-600'
                  : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'
                }
                ${feedbackGiven !== null && feedbackGiven !== 'not_helpful' ? 'opacity-30' : ''}
              `}
              title="无用"
            >
              👎 无用
            </button>
            <button
              onClick={handleCopy}
              className="rounded-full px-2 py-1 text-xs text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
              title="复制"
            >
              {copied ? '✓ 已复制' : '📋 复制'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(MessageBubble);
export { MessageBubble };

// Typing indicator component
interface TypingIndicatorProps {
  className?: string;
}

export function TypingIndicator({ className = '' }: TypingIndicatorProps) {
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-primary-500 text-white text-sm font-medium">
        🤖
      </div>
      <div className="bg-white rounded-2xl rounded-bl-md border border-gray-100 px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '0ms' }} />
          <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '150ms' }} />
          <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}
