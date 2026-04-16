'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface UseChatStreamOptions {
  url?: string;
  onMessage?: (message: ChatMessage) => void;
  onError?: (error: Error) => void;
  onConnectionChange?: (connected: boolean) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface ChatStreamState {
  isConnected: boolean;
  isConnecting: boolean;
  messages: ChatMessage[];
  error: Error | null;
}

export function useChatStream(options: UseChatStreamOptions = {}) {
  const {
    url = 'ws://localhost:8000/ws/chat',
    onMessage,
    onError,
    onConnectionChange,
    reconnectAttempts = 3,
    reconnectInterval = 3000,
  } = options;

  const [state, setState] = useState<ChatStreamState>({
    isConnected: false,
    isConnecting: false,
    messages: [],
    error: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (state.isConnecting || state.isConnected) return;

    setState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        if (!mountedRef.current) return;
        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
        }));
        reconnectCountRef.current = 0;
        onConnectionChange?.(true);
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const data = JSON.parse(event.data);

          if (data.type === 'message') {
            const message: ChatMessage = data.payload;
            setState(prev => ({
              ...prev,
              messages: [...prev.messages, message],
            }));
            onMessage?.(message);
          }

          if (data.type === 'stream_chunk') {
            // Handle streaming chunks
            const chunk = data.content || '';
            setState(prev => {
              const messages = [...prev.messages];
              const lastMessage = messages[messages.length - 1];
              
              if (lastMessage && lastMessage.role === 'assistant') {
                messages[messages.length - 1] = {
                  ...lastMessage,
                  content: lastMessage.content + chunk,
                };
              } else {
                messages.push({
                  role: 'assistant',
                  content: chunk,
                });
              }
              
              return { ...prev, messages };
            });

            onMessage?.({ role: 'assistant', content: chunk });
          }
        } catch (err) {
          console.error('Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
      };

      ws.onclose = (event) => {
        if (!mountedRef.current) return;

        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }));
        onConnectionChange?.(false);

        // Auto reconnect
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              reconnectCountRef.current += 1;
              connect();
            }
          }, reconnectInterval);
        } else {
          const error = new Error(`连接断开，已重试 ${reconnectAttempts} 次`);
          setState(prev => ({ ...prev, error }));
          onError?.(error);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error,
      }));
      onError?.(error);
    }
  }, [url, state.isConnecting, state.isConnected, reconnectAttempts, reconnectInterval, onMessage, onError, onConnectionChange]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    reconnectCountRef.current = reconnectAttempts; // Stop auto-reconnect

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setState(prev => ({ ...prev, isConnected: false, isConnecting: false }));
    onConnectionChange?.(false);
  }, [reconnectAttempts, onConnectionChange]);

  const sendMessage = useCallback((content: string, petId?: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket 未连接');
    }

    const userMessage: ChatMessage = { role: 'user', content };
    
    // Add user message to local state immediately
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
    }));

    // Send to server
    wsRef.current.send(JSON.stringify({
      type: 'chat',
      content,
      pet_id: petId,
    }));

    return userMessage;
  }, []);

  const clearMessages = useCallback(() => {
    setState(prev => ({ ...prev, messages: [] }));
  }, []);

  // Connect on mount
  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage,
    clearMessages,
  };
}

// SSE fallback for environments without WebSocket support
export function useSSEChat(url: string = '/api/v1/chat') {
  const [isStreaming, setIsStreaming] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string, petId?: string) => {
    setIsStreaming(true);
    setError(null);

    // Add user message
    const userMessage: ChatMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);

    try {
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, pet_id: petId }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response reader');

      const decoder = new TextDecoder();
      let assistantContent = '';

      let isReading = true;
      while (isReading) {
        const { done, value } = await reader.read();
        if (done) {
          isReading = false;
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        
        // Parse SSE format
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                assistantContent += parsed.content;
                setMessages(prev => {
                  const msgs = [...prev];
                  const lastMsg = msgs[msgs.length - 1];
                  
                  if (lastMsg && lastMsg.role === 'assistant') {
                    msgs[msgs.length - 1] = { ...lastMsg, content: assistantContent };
                  } else {
                    msgs.push({ role: 'assistant', content: assistantContent });
                  }
                  
                  return msgs;
                });
              }
            } catch {
              // Ignore parse errors for partial data
            }
          }
        }
      }

      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: assistantContent },
      ]);
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [url]);

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    isStreaming,
    messages,
    error,
    sendMessage,
    stopStreaming,
    clearMessages,
  };
}
